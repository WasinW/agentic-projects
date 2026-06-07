# Complete Execution Flow for Order Flow Trading System

> **Axis 1 — Trading Strategies | Module 03 — Order Flow & Liquidity**
> Document: 05_execution_flow.md
> Version: 2.0 | Last Updated: 2026-04-12
> Classification: Core Knowledge Base — Multi-Agent AI Trading System

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Step-by-Step Algorithm](#2-step-by-step-algorithm)
3. [Data Requirements](#3-data-requirements)
4. [Signal Generation Pipeline](#4-signal-generation-pipeline)
5. [Risk Parameters for Order Flow Strategies](#5-risk-parameters-for-order-flow-strategies)
6. [Position Sizing Models](#6-position-sizing-models)
7. [Pseudocode for Full Implementation](#7-pseudocode-for-full-implementation)
8. [Latency Considerations: Crypto vs Forex](#8-latency-considerations-crypto-vs-forex)
9. [System Architecture](#9-system-architecture)
10. [Backtesting Framework](#10-backtesting-framework)
11. [Monitoring & Alerting](#11-monitoring--alerting)
12. [Performance Metrics](#12-performance-metrics)
13. [Failure Modes & Recovery](#13-failure-modes--recovery)
14. [Deployment Configuration](#14-deployment-configuration)
15. [References](#15-references)

---

## 1. Introduction

### 1.1 Purpose

This document provides the complete, production-ready execution flow for the Order Flow & Liquidity trading system. It integrates all concepts from Documents 00-04 into a unified pipeline that can be implemented as part of the Multi-Agent AI Trading System.

### 1.2 System Scope

```
SYSTEM BOUNDARY:
═══════════════

INPUTS:                          SYSTEM:                    OUTPUTS:
─────────                        ───────                    ────────
┌──────────────┐    ┌─────────────────────────────────┐    ┌──────────┐
│ Market Data  │───►│                                 │───►│ Orders   │
│ • L2 Book   │    │    ORDER FLOW TRADING ENGINE     │    │ • Entry  │
│ • Trades    │    │                                 │    │ • Exit   │
│ • Tick Data │    │  ┌───────────────────────────┐  │    │ • Modify │
│              │    │  │ Signal Generation Layer   │  │    └──────────┘
│ Config/State │───►│  │ • Book Analysis (Doc 01)  │  │
│ • Parameters│    │  │ • Liquidity Map (Doc 02)  │  │    ┌──────────┐
│ • Positions │    │  │ • Hunt Detection (Doc 03) │  │───►│ Logs &   │
│ • Risk State│    │  │ • Volume Delta (Doc 04)   │  │    │ Metrics  │
│              │    │  └───────────────────────────┘  │    └──────────┘
│ External    │───►│  ┌───────────────────────────┐  │
│ • Calendar  │    │  │ Decision & Risk Layer     │  │    ┌──────────┐
│ • Sessions  │    │  │ • Signal aggregation      │  │───►│ Alerts   │
│ • Other Mods│    │  │ • Risk management         │  │    └──────────┘
└──────────────┘    │  │ • Position sizing         │  │
                    │  └───────────────────────────┘  │
                    │  ┌───────────────────────────┐  │
                    │  │ Execution Layer           │  │
                    │  │ • Order routing           │  │
                    │  │ • Slippage control        │  │
                    │  │ • Fill management         │  │
                    │  └───────────────────────────┘  │
                    └─────────────────────────────────┘
```

### 1.3 Operating Modes

| Mode | Description | Data Source | Latency Target |
|------|-------------|-------------|---------------|
| **Live Trading** | Real-time execution against live market | Exchange feeds | <100ms end-to-end |
| **Paper Trading** | Simulated execution with live data | Exchange feeds | <100ms (same pipeline) |
| **Backtesting** | Historical simulation | Stored tick/L2 data | As fast as possible |
| **Research** | Strategy development and analysis | Historical + simulated | N/A |

---

## 2. Step-by-Step Algorithm

### 2.1 High-Level Flow

```
┌────────────────────────────────────────────────────────────────────┐
│ STEP 1: PRE-SESSION PREPARATION                                     │
│ • Determine HTF bias (Daily/Weekly structure)                       │
│ • Map liquidity pools (BSL/SSL) on 4H/1D                          │
│ • Identify active FVGs, OBs, Breakers on 4H/1H                    │
│ • Note key time events (news, session opens)                        │
│ • Set kill zone schedule                                            │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 2: DATA INGESTION (Continuous)                                 │
│ • Receive L2 order book updates                                     │
│ • Receive trade feed (Time & Sales)                                 │
│ • Update VWAP, Volume Profile, Delta continuously                   │
│ • Rebuild order book state on each update                           │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 3: SIGNAL GENERATION (On each update/bar close)                │
│                                                                     │
│ 3a. Order Book Signals:                                             │
│     • Weighted imbalance                                            │
│     • Wall detection                                                │
│     • Absorption patterns                                           │
│     • Spoofing detection                                            │
│     • Iceberg detection                                             │
│                                                                     │
│ 3b. Liquidity Signals:                                              │
│     • BSL/SSL proximity and sweep detection                         │
│     • FVG formation and fill tracking                               │
│     • OTE zone price entry                                          │
│     • Breaker Block test                                            │
│                                                                     │
│ 3c. Institutional Flow Signals:                                     │
│     • Judas Swing detection                                         │
│     • AMD phase identification                                      │
│     • Kill zone timing confirmation                                 │
│     • Stop hunt detection                                           │
│                                                                     │
│ 3d. Volume Delta Signals:                                           │
│     • Per-bar delta direction                                       │
│     • CVD divergence                                                │
│     • Delta exhaustion                                              │
│     • VWAP position                                                 │
│     • Volume Profile (POC/VA) analysis                              │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 4: SIGNAL AGGREGATION & SCORING                                │
│ • Combine all signals into composite direction score                │
│ • Apply HTF bias filter (reject signals against HTF trend)          │
│ • Apply kill zone filter (reject signals outside active zones)      │
│ • Calculate confluence score                                        │
│ • Compare against minimum threshold                                 │
│ • Rank competing signals by quality                                 │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 5: RISK VALIDATION                                             │
│ • Check daily loss limit (not exceeded)                             │
│ • Check max open positions                                          │
│ • Check correlation with existing positions                         │
│ • Validate R:R meets minimum (>2:1)                                │
│ • Calculate position size                                           │
│ • Verify sufficient margin/capital                                  │
│ • Check news calendar (no high-impact within buffer)                │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 6: ORDER EXECUTION                                             │
│ • Determine order type (limit vs market)                            │
│ • Set entry price (CE of FVG, OTE level, etc.)                     │
│ • Set stop loss (anti-hunt placement)                               │
│ • Set take profit levels (TP1, TP2, TP3)                           │
│ • Submit order to exchange                                          │
│ • Confirm fill                                                      │
│ • Start position monitoring                                         │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 7: POSITION MANAGEMENT (Continuous while position open)        │
│ • Monitor for exit signals                                          │
│ • Manage partial exits at TP levels                                 │
│ • Adjust trailing stop based on order flow                          │
│ • Monitor for adverse signals (delta flip, opposing absorption)     │
│ • Time-based management (end of session, kill zone exit)            │
│ • Emergency exit on spread blowout or liquidity crisis              │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ STEP 8: POST-TRADE ANALYSIS & LOGGING                               │
│ • Record all trade parameters and outcomes                          │
│ • Update performance metrics                                        │
│ • Evaluate signal quality (was the signal correct?)                 │
│ • Feed results back for parameter optimization                      │
│ • Generate daily/weekly performance reports                          │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Decision Tree

```python
def main_decision_flow(state: SystemState) -> Action:
    """
    Top-level decision tree for the order flow trading system.
    Called on each significant market update.
    """
    
    # GATE 1: Are we in an active trading period?
    if not state.kill_zone_active:
        if state.has_open_positions:
            return manage_positions_passively(state)
        return Action.WAIT
    
    # GATE 2: Are risk limits intact?
    if state.daily_loss_exceeded or state.max_positions_reached:
        if state.has_open_positions:
            return manage_positions_defensively(state)
        return Action.WAIT
    
    # GATE 3: Is there a tradeable signal?
    signal = state.best_signal
    if not signal or signal.confluence_score < state.config.min_confluence:
        if state.has_open_positions:
            return manage_positions_normally(state)
        return Action.WAIT
    
    # GATE 4: Does signal align with HTF bias?
    if not signal_aligns_with_bias(signal, state.htf_bias):
        return Action.WAIT
    
    # GATE 5: Is R:R acceptable?
    trade_params = calculate_trade_params(signal, state)
    if trade_params.risk_reward < state.config.min_rr:
        return Action.WAIT
    
    # GATE 6: No conflicting news?
    if high_impact_news_imminent(state.calendar, buffer_minutes=15):
        return Action.WAIT
    
    # ALL GATES PASSED → EXECUTE
    return Action.ENTER_TRADE(trade_params)
```

---

## 3. Data Requirements

### 3.1 Data Types and Sources

| Data Type | Description | Source (Forex) | Source (Crypto) | Update Rate |
|-----------|-------------|---------------|----------------|-------------|
| **L2 Order Book** | Resting orders at each price level | CME MDP 3.0, ECN feeds | Exchange WebSocket (depth) | 10-100ms |
| **Trade Feed** | Individual executed trades with aggressor | CME, broker feed | Exchange WebSocket (trade) | Real-time |
| **OHLCV Bars** | Aggregated price/volume data | Broker API, TradingView | Exchange REST/WS | Per-bar |
| **Tick Data** | Every price change | CQG, TrueFX | Exchange trade stream | Real-time |
| **Funding Rate** | Perpetual swap funding | N/A | Exchange API | 8-hourly |
| **Open Interest** | Total open contracts | CME | Exchange API | 1-5min |
| **Liquidation Data** | Forced closures | N/A | Exchange WS (optional) | Real-time |
| **Economic Calendar** | Scheduled news events | ForexFactory, Investing.com | API | Static + alerts |
| **Session Times** | Market session boundaries | Static configuration | Static configuration | Static |

### 3.2 Data Quality Requirements

| Metric | Requirement | Impact if Not Met |
|--------|-------------|-------------------|
| **Latency** | <50ms from exchange to signal | Stale signals, worse fills |
| **Completeness** | >99.9% message delivery | Missing trades → wrong delta |
| **Sequence** | Monotonically increasing timestamps | Incorrect state reconstruction |
| **Accuracy** | No duplicate trades | Inflated delta values |
| **Uptime** | >99.5% feed availability | Blind periods, missed signals |

### 3.3 Data Storage Schema

```sql
-- Trades table (primary data source for delta)
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price DECIMAL(20, 10) NOT NULL,
    quantity DECIMAL(20, 10) NOT NULL,
    side VARCHAR(4) NOT NULL,  -- 'BUY' or 'SELL'
    trade_id VARCHAR(50),
    
    -- Indexes for fast querying
    INDEX idx_symbol_time (symbol, timestamp),
    INDEX idx_exchange_symbol (exchange, symbol)
);

-- Order book snapshots (for replay/backtesting)
CREATE TABLE order_book_snapshots (
    id BIGSERIAL PRIMARY KEY,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    bids JSONB NOT NULL,  -- [[price, quantity], ...]
    asks JSONB NOT NULL,  -- [[price, quantity], ...]
    
    INDEX idx_symbol_time (symbol, timestamp)
);

-- Signals generated
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    direction VARCHAR(5) NOT NULL,
    strength DECIMAL(5, 4) NOT NULL,
    confluence_score DECIMAL(5, 4),
    parameters JSONB,
    acted_on BOOLEAN DEFAULT FALSE,
    outcome VARCHAR(20),  -- 'WIN', 'LOSS', 'BREAKEVEN', NULL
    
    INDEX idx_symbol_time (symbol, timestamp)
);

-- Positions and trades
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(5) NOT NULL,
    entry_price DECIMAL(20, 10),
    entry_time TIMESTAMPTZ,
    exit_price DECIMAL(20, 10),
    exit_time TIMESTAMPTZ,
    size DECIMAL(20, 10),
    stop_loss DECIMAL(20, 10),
    take_profit DECIMAL(20, 10),
    status VARCHAR(20),  -- 'OPEN', 'CLOSED', 'CANCELLED'
    pnl DECIMAL(20, 10),
    pnl_pct DECIMAL(10, 6),
    signal_id BIGINT REFERENCES signals(id),
    metadata JSONB
);
```

### 3.4 Historical Data Requirements for Backtesting

| Asset | Minimum History | Ideal History | Data Resolution |
|-------|----------------|---------------|-----------------|
| Forex Major | 2 years | 5-10 years | Tick data or 1-second bars |
| Forex Cross | 2 years | 5 years | 1-minute bars minimum |
| BTC/USDT | 2 years | 4-5 years (since liquid) | Tick data preferred |
| ETH/USDT | 2 years | 3-4 years | Tick data preferred |
| Altcoins | 1 year | 2 years | 1-minute bars minimum |

---

## 4. Signal Generation Pipeline

### 4.1 Pipeline Architecture

```
RAW DATA STREAMS
      │
      ├── L2 Book Updates ──┐
      │                      │
      ├── Trade Feed ────────┤
      │                      │
      ├── Bar Close ─────────┤
      │                      │
      ▼                      ▼
┌─────────────────────────────────────────────────┐
│          DATA NORMALIZATION LAYER                 │
│  • Timestamp alignment                           │
│  • Symbol normalization                          │
│  • Unit conversion (lots/contracts/coins)        │
│  • Duplicate detection and removal               │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│          FEATURE CALCULATION LAYER               │
│                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Order Book  │ │   Delta     │ │  Volume   │ │
│  │ Features    │ │  Features   │ │  Profile  │ │
│  │             │ │             │ │  Features │ │
│  │ • Imbalance │ │ • Bar delta │ │ • POC     │ │
│  │ • Walls     │ │ • CVD      │ │ • VAH/VAL │ │
│  │ • Spread    │ │ • Delta ROC│ │ • HVN/LVN │ │
│  │ • Depth     │ │ • Strength │ │           │ │
│  │ • Entropy   │ │ • BVC      │ │           │ │
│  └──────┬──────┘ └──────┬─────┘ └─────┬─────┘ │
│         │               │             │         │
│  ┌──────┴──────┐ ┌──────┴─────┐ ┌─────┴─────┐ │
│  │ Liquidity  │ │    VWAP    │ │  Session  │ │
│  │ Features   │ │  Features  │ │  Features │ │
│  │             │ │            │ │           │ │
│  │ • BSL/SSL  │ │ • Value    │ │ • KZ flag │ │
│  │ • FVG list │ │ • Z-score  │ │ • AMD     │ │
│  │ • OTE zone │ │ • Bands    │ │ • Judas   │ │
│  │ • Breakers │ │ • Anchored │ │ • Phase   │ │
│  └──────┬──────┘ └──────┬─────┘ └─────┬─────┘ │
└─────────┼───────────────┼─────────────┼────────┘
          │               │             │
          ▼               ▼             ▼
┌─────────────────────────────────────────────────┐
│          SIGNAL DETECTION LAYER                  │
│                                                 │
│  Each feature set generates independent signals: │
│                                                 │
│  • Book Imbalance Signal (direction + strength) │
│  • Absorption Signal (level + direction)         │
│  • Delta Divergence Signal (type + strength)     │
│  • FVG Entry Signal (level + direction)          │
│  • Stop Hunt Signal (direction + confidence)     │
│  • Judas Swing Signal (direction + target)       │
│  • VWAP Extreme Signal (direction + target)      │
│  • POC Test Signal (direction + level)           │
│  • Exhaustion Signal (direction + strength)      │
│                                                 │
└──────────────────────┬──────────────────────────┘
                       │ List of independent signals
                       ▼
┌─────────────────────────────────────────────────┐
│          SIGNAL AGGREGATION LAYER                │
│                                                 │
│  1. Filter by direction (must agree with HTF)    │
│  2. Filter by kill zone (must be active)         │
│  3. Filter by minimum strength                   │
│  4. Calculate confluence (signals at same level) │
│  5. Score composite direction                    │
│  6. Select best opportunity                      │
│                                                 │
│  OUTPUT: Final Trade Signal                      │
│  • Direction: LONG / SHORT / NEUTRAL             │
│  • Entry Level                                   │
│  • Confidence Score [0, 1]                       │
│  • Contributing Signals (for logging)            │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
              [Risk & Execution Layer]
```

### 4.2 Signal Aggregation Logic

```python
class SignalAggregator:
    """
    Combines multiple independent signals into a final trade decision.
    """
    
    # Signal weights (must sum to 1.0)
    SIGNAL_WEIGHTS = {
        'STOP_HUNT': 0.20,          # Highest weight — institutional alignment
        'CVD_DIVERGENCE': 0.18,     # Strong leading signal
        'JUDAS_SWING': 0.15,        # High-probability pattern
        'FVG_ENTRY': 0.12,          # Structural level
        'DELTA_EXHAUSTION': 0.10,   # Momentum exhaustion
        'BOOK_IMBALANCE': 0.08,     # Short-term pressure
        'ABSORPTION': 0.07,         # Level defense
        'VWAP_EXTREME': 0.05,       # Mean reversion
        'POC_TEST': 0.05,           # Value area test
    }
    
    def __init__(self, config):
        self.min_confluence = config.get('min_confluence_score', 0.55)
        self.min_signals = config.get('min_concurrent_signals', 2)
        self.htf_bias = None
        self.kill_zone_active = False
    
    def aggregate(self, signals: List[dict], htf_bias: str, 
                  kill_zone: bool) -> Optional[dict]:
        """
        Aggregate multiple signals into a final trade decision.
        
        Args:
            signals: List of signal dicts with 'type', 'direction', 'strength'
            htf_bias: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            kill_zone: Whether we're in an active kill zone
        
        Returns:
            Final aggregated signal or None
        """
        self.htf_bias = htf_bias
        self.kill_zone_active = kill_zone
        
        if not signals:
            return None
        
        # FILTER 1: Kill Zone
        if not kill_zone:
            return None
        
        # FILTER 2: HTF Alignment
        aligned_signals = []
        for signal in signals:
            if htf_bias == 'NEUTRAL':
                aligned_signals.append(signal)  # Allow any direction
            elif signal['direction'] == ('LONG' if htf_bias == 'BULLISH' else 'SHORT'):
                aligned_signals.append(signal)
            # Special case: counter-trend signals require higher strength
            elif signal['strength'] > 0.8:
                signal['strength'] *= 0.7  # Reduce weight for counter-trend
                aligned_signals.append(signal)
        
        if not aligned_signals:
            return None
        
        # FILTER 3: Minimum signal count
        if len(aligned_signals) < self.min_signals:
            return None
        
        # CALCULATE CONFLUENCE SCORE
        direction_scores = {'LONG': 0.0, 'SHORT': 0.0}
        
        for signal in aligned_signals:
            weight = self.SIGNAL_WEIGHTS.get(signal['type'], 0.05)
            score_contribution = weight * signal['strength']
            direction_scores[signal['direction']] += score_contribution
        
        # Determine winning direction
        if direction_scores['LONG'] > direction_scores['SHORT']:
            final_direction = 'LONG'
            final_score = direction_scores['LONG']
        else:
            final_direction = 'SHORT'
            final_score = direction_scores['SHORT']
        
        # Normalize score
        max_possible = sum(self.SIGNAL_WEIGHTS.values())
        confluence_score = final_score / max_possible
        
        # FILTER 4: Minimum confluence
        if confluence_score < self.min_confluence:
            return None
        
        # Determine entry level (consensus of signal levels)
        entry_levels = [
            s.get('entry_level', s.get('level')) 
            for s in aligned_signals 
            if s['direction'] == final_direction and s.get('entry_level') or s.get('level')
        ]
        
        entry_level = np.median(entry_levels) if entry_levels else None
        
        return {
            'direction': final_direction,
            'confluence_score': confluence_score,
            'entry_level': entry_level,
            'contributing_signals': [
                {'type': s['type'], 'strength': s['strength'], 'direction': s['direction']}
                for s in aligned_signals if s['direction'] == final_direction
            ],
            'opposing_signals': [
                {'type': s['type'], 'strength': s['strength']}
                for s in aligned_signals if s['direction'] != final_direction
            ],
            'signal_count': len([s for s in aligned_signals if s['direction'] == final_direction]),
            'htf_aligned': htf_bias != 'NEUTRAL' and final_direction == ('LONG' if htf_bias == 'BULLISH' else 'SHORT'),
            'timestamp': time.time()
        }
```

### 4.3 Signal Priority Rules

When multiple valid signals exist simultaneously:

| Priority | Rule | Rationale |
|----------|------|-----------|
| 1 | Highest confluence score wins | More confirmation = higher probability |
| 2 | On tie: HTF-aligned signal wins | Trading with the trend is safer |
| 3 | On tie: Signal with better R:R wins | Better reward per unit risk |
| 4 | On tie: Signal closer to entry level wins | Quicker execution |
| 5 | On tie: First signal in time wins | Earliest detection advantage |

---

## 5. Risk Parameters for Order Flow Strategies

### 5.1 Account-Level Risk Controls

```python
class RiskManager:
    """
    Manages all risk parameters for the order flow trading system.
    """
    
    # Account-level limits
    MAX_DAILY_LOSS_PCT = 0.04          # 4% max daily loss
    MAX_WEEKLY_LOSS_PCT = 0.08         # 8% max weekly loss
    MAX_MONTHLY_LOSS_PCT = 0.15        # 15% max monthly loss
    MAX_OPEN_POSITIONS = 3             # Max simultaneous positions
    MAX_CORRELATED_POSITIONS = 2       # Max positions in correlated pairs
    MAX_SINGLE_TRADE_RISK_PCT = 0.02   # 2% max risk per trade
    DEFAULT_TRADE_RISK_PCT = 0.01      # 1% default risk per trade
    
    # Strategy-specific limits
    STRATEGY_LIMITS = {
        'STOP_HUNT_REVERSAL': {'max_risk': 0.015, 'max_positions': 2, 'min_rr': 2.5},
        'CVD_DIVERGENCE': {'max_risk': 0.015, 'max_positions': 2, 'min_rr': 2.0},
        'JUDAS_SWING': {'max_risk': 0.020, 'max_positions': 1, 'min_rr': 3.0},
        'FVG_ENTRY': {'max_risk': 0.010, 'max_positions': 3, 'min_rr': 2.0},
        'VWAP_REVERSION': {'max_risk': 0.010, 'max_positions': 2, 'min_rr': 1.5},
        'BOOK_IMBALANCE': {'max_risk': 0.005, 'max_positions': 2, 'min_rr': 1.5},
    }
    
    def __init__(self, config):
        self.account_equity = config['initial_equity']
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.open_positions = []
        self.consecutive_losses = 0
        self.today_trades = 0
    
    def can_open_position(self, strategy_type: str = None) -> dict:
        """
        Check if a new position can be opened.
        Returns dict with 'allowed' bool and 'reason' if not.
        """
        # Check daily loss
        if abs(self.daily_pnl) / self.account_equity > self.MAX_DAILY_LOSS_PCT:
            return {'allowed': False, 'reason': 'Daily loss limit reached'}
        
        # Check weekly loss
        if abs(self.weekly_pnl) / self.account_equity > self.MAX_WEEKLY_LOSS_PCT:
            return {'allowed': False, 'reason': 'Weekly loss limit reached'}
        
        # Check max positions
        if len(self.open_positions) >= self.MAX_OPEN_POSITIONS:
            return {'allowed': False, 'reason': 'Max positions reached'}
        
        # Check strategy-specific limits
        if strategy_type and strategy_type in self.STRATEGY_LIMITS:
            limit = self.STRATEGY_LIMITS[strategy_type]
            strategy_positions = [
                p for p in self.open_positions 
                if p.strategy_type == strategy_type
            ]
            if len(strategy_positions) >= limit['max_positions']:
                return {'allowed': False, 'reason': f'Max {strategy_type} positions reached'}
        
        # Check consecutive losses (reduce size after 3+)
        if self.consecutive_losses >= 5:
            return {'allowed': False, 'reason': 'Too many consecutive losses — pause trading'}
        
        return {'allowed': True, 'reason': None}
    
    def calculate_position_size(self, entry: float, stop: float, 
                                 strategy_type: str,
                                 signal_strength: float,
                                 kill_zone_multiplier: float = 1.0) -> float:
        """
        Calculate optimal position size based on risk parameters.
        
        Formula: Size = Risk$ / SL_Distance
        Adjusted by: signal strength, kill zone, consecutive losses
        """
        # Base risk per trade
        limits = self.STRATEGY_LIMITS.get(strategy_type, {})
        max_risk_pct = limits.get('max_risk', self.DEFAULT_TRADE_RISK_PCT)
        
        # Adjust risk based on signal strength
        adjusted_risk_pct = max_risk_pct * signal_strength
        
        # Reduce after consecutive losses
        if self.consecutive_losses >= 3:
            adjusted_risk_pct *= 0.5
        elif self.consecutive_losses >= 2:
            adjusted_risk_pct *= 0.75
        
        # Apply kill zone multiplier
        adjusted_risk_pct *= kill_zone_multiplier
        
        # Cap at maximum
        adjusted_risk_pct = min(adjusted_risk_pct, self.MAX_SINGLE_TRADE_RISK_PCT)
        
        # Calculate dollar risk
        risk_dollars = self.account_equity * adjusted_risk_pct
        
        # Calculate stop distance
        sl_distance = abs(entry - stop)
        
        if sl_distance == 0:
            return 0.0
        
        # Position size in units
        position_size = risk_dollars / sl_distance
        
        return position_size
```

### 5.2 Per-Trade Risk Framework

```
RISK CALCULATION FLOW:
═══════════════════════

                    Account Equity: $100,000
                           │
                           ▼
            ┌──────────────────────────────┐
            │ Base Risk: 1% = $1,000       │
            └──────────────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
              ▼            ▼                ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ Signal      │ │ Kill Zone   │ │ Consecutive │
    │ Strength    │ │ Multiplier  │ │ Loss Adj    │
    │             │ │             │ │             │
    │ 0.8 = 80%  │ │ London=1.5x│ │ 0 losses=1x│
    │             │ │ NY=1.3x    │ │ 2 losses=.75│
    │             │ │ Asian=0.7x │ │ 3+ loss=.5x│
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────────────────────────────────────┐
    │ Adjusted Risk = $1,000 * 0.8 * 1.5 * 1.0   │
    │              = $1,200                        │
    └──────────────────────┬──────────────────────┘
                           │
                           ▼
    ┌─────────────────────────────────────────────┐
    │ SL Distance = |Entry - Stop| = 30 pips     │
    │ Pip Value = $10 per pip (standard lot)      │
    │                                             │
    │ Position Size = $1,200 / (30 * $10)         │
    │              = 4.0 mini lots                 │
    │              = 0.40 standard lots            │
    └─────────────────────────────────────────────┘
```

---

## 6. Position Sizing Models

### 6.1 Fixed Fractional Model (Default)

$$\text{Size} = \frac{f \cdot E}{|P_{entry} - P_{stop}| \cdot \text{PipValue}}$$

Where:
- $f$ = Risk fraction (0.01-0.02)
- $E$ = Current account equity
- $P_{entry}$ = Entry price
- $P_{stop}$ = Stop loss price
- PipValue = Dollar value per pip for the instrument

### 6.2 Kelly Criterion (Aggressive — Use with Caution)

$$f^* = \frac{p \cdot b - q}{b}$$

Where:
- $p$ = Win probability (from backtesting)
- $q$ = 1 - p (loss probability)
- $b$ = Win/Loss ratio (average win / average loss)

**In practice, use fractional Kelly (25-50% of Kelly optimal) to reduce variance:**

$$f_{practical} = 0.25 \cdot f^*$$

### 6.3 Volatility-Adjusted Position Sizing

$$\text{Size} = \frac{f \cdot E}{\text{ATR}_{14} \cdot \text{ATR\_Multiple} \cdot \text{PipValue}}$$

This automatically sizes positions smaller in volatile markets and larger in calm markets.

### 6.4 Liquidity-Constrained Position Sizing

$$\text{Size} = \min\left(\text{Size}_{risk}, \text{ADV} \cdot \text{MaxParticipation}\right)$$

Where:
- $\text{ADV}$ = Average Daily Volume
- MaxParticipation = Maximum percentage of daily volume (1-5%)

This prevents the system from taking positions too large relative to available liquidity.

### 6.5 Implementation

```python
class PositionSizer:
    """
    Calculates position size using multiple models and constraints.
    """
    
    def __init__(self, config):
        self.model = config.get('sizing_model', 'FIXED_FRACTIONAL')
        self.max_participation = config.get('max_participation', 0.03)
        self.kelly_fraction = config.get('kelly_fraction', 0.25)
    
    def calculate(self, equity: float, entry: float, stop: float,
                  pip_value: float, atr: float, adv: float,
                  win_rate: float = None, payoff_ratio: float = None,
                  signal_strength: float = 1.0) -> dict:
        """
        Calculate position size using configured model.
        """
        # Fixed fractional (base calculation)
        risk_fraction = 0.01 * signal_strength  # 1% adjusted by signal
        sl_distance = abs(entry - stop)
        
        if sl_distance == 0 or pip_value == 0:
            return {'size': 0, 'risk_dollars': 0, 'model': 'ZERO_SL'}
        
        risk_dollars = equity * risk_fraction
        size_risk = risk_dollars / (sl_distance * pip_value)
        
        # Kelly (if historical stats available)
        if self.model == 'KELLY' and win_rate and payoff_ratio:
            kelly_f = (win_rate * payoff_ratio - (1 - win_rate)) / payoff_ratio
            kelly_f = max(0, kelly_f) * self.kelly_fraction  # Fractional Kelly
            size_kelly = (equity * kelly_f) / (sl_distance * pip_value)
            size_risk = min(size_risk, size_kelly)
        
        # Volatility adjustment
        if self.model == 'VOLATILITY_ADJUSTED':
            vol_size = (equity * risk_fraction) / (atr * 2.0 * pip_value)
            size_risk = min(size_risk, vol_size)
        
        # Liquidity constraint
        size_liquidity = adv * self.max_participation if adv > 0 else float('inf')
        
        # Final size = minimum of all constraints
        final_size = min(size_risk, size_liquidity)
        final_size = max(final_size, 0)  # No negative sizes
        
        return {
            'size': round(final_size, 2),
            'risk_dollars': risk_dollars,
            'risk_pct': risk_fraction * 100,
            'sl_distance': sl_distance,
            'model': self.model,
            'liquidity_constrained': final_size == size_liquidity
        }
```

---

## 7. Pseudocode for Full Implementation

### 7.1 Complete System Implementation

```python
"""
ORDER FLOW TRADING SYSTEM — COMPLETE IMPLEMENTATION
===================================================

This module implements the full order flow trading system,
integrating all components from Documents 00-04.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from collections import deque
import numpy as np

# Internal modules (from Documents 00-04)
from .order_book_analyzer import OrderBookAnalyzer, OrderBookState
from .liquidity_mapper import LiquidityMapper, LiquidityPool, FVGDetector
from .stop_hunt_detector import StopHuntDetector, JudasSwingDetector
from .volume_delta import DeltaCalculator, CVDDivergenceDetector, VWAP, VolumeProfileBuilder
from .kill_zones import KillZoneManager
from .risk_manager import RiskManager, PositionSizer
from .signal_aggregator import SignalAggregator
from .execution import OrderExecutor
from .data_feed import DataFeed, CandleStore


@dataclass
class SystemConfig:
    """Configuration for the order flow trading system."""
    # Market
    symbol: str = 'EUR/USD'
    market_type: str = 'FOREX'  # 'FOREX' or 'CRYPTO'
    
    # Timeframes
    htf_timeframe: str = '1D'      # Higher timeframe for bias
    mtf_timeframe: str = '4H'      # Medium timeframe for structure
    entry_timeframe: str = '1H'    # Entry timeframe
    precision_timeframe: str = '15M'  # Precision timing
    
    # Signal thresholds
    min_confluence_score: float = 0.55
    min_signal_strength: float = 0.5
    min_risk_reward: float = 2.0
    min_concurrent_signals: int = 2
    
    # Risk
    risk_per_trade: float = 0.01   # 1%
    max_daily_loss: float = 0.04   # 4%
    max_positions: int = 3
    
    # Execution
    use_limit_orders: bool = True
    max_slippage_pips: float = 2.0
    order_timeout_seconds: float = 300.0
    
    # Session
    kill_zone_only: bool = True
    news_buffer_minutes: int = 15


class OrderFlowTradingSystem:
    """
    Main class implementing the complete order flow trading system.
    
    Lifecycle:
    1. Initialize → configure all sub-systems
    2. Pre-Session Analysis → set bias, map liquidity
    3. Main Loop → process data, generate signals, execute trades
    4. Shutdown → close positions, cleanup
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.logger = logging.getLogger('OrderFlowSystem')
        
        # Sub-systems
        self.book_analyzer = OrderBookAnalyzer({
            'imbalance_levels': 10,
            'imbalance_decay': 0.3,
            'imbalance_threshold': 0.4,
            'wall_threshold': 3.0,
        })
        
        self.liquidity_mapper = LiquidityMapper({
            'swing_lookback': 5,
            'equal_high_tolerance_pct': 0.05,
            'equal_low_tolerance_pct': 0.05,
        })
        
        self.fvg_detector = FVGDetector({
            'min_gap_atr_ratio': 0.5,
            'timeframe': config.entry_timeframe,
        })
        
        self.hunt_detector = StopHuntDetector({
            'max_exceedance_bars': 3,
            'confirmation_bars': 2,
        })
        
        self.judas_detector = JudasSwingDetector({
            'judas_window_minutes': 90,
        })
        
        self.delta_calc = DeltaCalculator({
            'bar_timeframe_s': self._timeframe_to_seconds(config.entry_timeframe),
        })
        
        self.cvd_detector = CVDDivergenceDetector({
            'min_swing_bars': 5,
            'divergence_lookback': 50,
        })
        
        self.vwap = VWAP(anchor_type='SESSION')
        self.volume_profile = VolumeProfileBuilder({})
        
        self.kill_zone_mgr = KillZoneManager(config.market_type)
        self.signal_aggregator = SignalAggregator({
            'min_confluence_score': config.min_confluence_score,
            'min_concurrent_signals': config.min_concurrent_signals,
        })
        
        self.risk_mgr = RiskManager({
            'initial_equity': 100000,  # Set from account
            'max_daily_loss': config.max_daily_loss,
            'max_positions': config.max_positions,
        })
        
        self.position_sizer = PositionSizer({
            'sizing_model': 'FIXED_FRACTIONAL',
            'max_participation': 0.03,
        })
        
        self.executor = OrderExecutor({
            'use_limit_orders': config.use_limit_orders,
            'max_slippage': config.max_slippage_pips,
        })
        
        # State
        self.candle_stores = {}
        self.htf_bias = 'NEUTRAL'
        self.session_analysis = None
        self.is_running = False
        self.current_session_date = None
    
    async def start(self, data_feed: DataFeed):
        """Start the trading system."""
        self.is_running = True
        self.logger.info(f"Starting Order Flow Trading System for {self.config.symbol}")
        
        # Initialize candle stores
        for tf in [self.config.htf_timeframe, self.config.mtf_timeframe,
                   self.config.entry_timeframe, self.config.precision_timeframe]:
            self.candle_stores[tf] = CandleStore(tf, max_candles=500)
        
        # Load historical data for initial state
        await self._load_initial_state(data_feed)
        
        # Main processing loop
        try:
            await self._main_loop(data_feed)
        except Exception as e:
            self.logger.error(f"System error: {e}", exc_info=True)
            await self._emergency_shutdown()
    
    async def _main_loop(self, data_feed: DataFeed):
        """Main processing loop — the heart of the system."""
        
        async for event in data_feed.stream():
            if not self.is_running:
                break
            
            current_time = datetime.fromtimestamp(event.timestamp, tz=timezone.utc)
            
            # === SESSION CHECK ===
            if self._is_new_session(current_time):
                await self._run_pre_session_analysis(data_feed, current_time)
            
            # === PROCESS EVENT ===
            if event.type == 'BOOK_UPDATE':
                self._process_book_update(event)
            
            elif event.type == 'TRADE':
                self._process_trade(event)
            
            elif event.type == 'BAR_CLOSE':
                await self._process_bar_close(event, data_feed, current_time)
    
    def _process_book_update(self, event):
        """Process L2 order book update."""
        book_state = OrderBookState(
            bids=event.bids,
            asks=event.asks,
            timestamp=event.timestamp
        )
        self.book_analyzer.update(book_state)
    
    def _process_trade(self, event):
        """Process individual trade (Time & Sales)."""
        # Update delta
        self.delta_calc.on_trade(
            price=event.price,
            volume=event.volume,
            side=event.side,
            timestamp=event.timestamp
        )
        
        # Update VWAP
        self.vwap.update(event.price, event.volume)
        
        # Update volume profile
        self.volume_profile.add_trade(event)
    
    async def _process_bar_close(self, event, data_feed, current_time):
        """
        Process bar close — main signal generation and decision point.
        This is where all analysis converges.
        """
        timeframe = event.timeframe
        
        # Update candle store
        self.candle_stores[timeframe].add_candle(event.candle)
        
        # Only generate signals on entry timeframe bar close
        if timeframe != self.config.entry_timeframe:
            return
        
        candles = self.candle_stores[timeframe].get_candles()
        current_price = candles[-1].close
        
        # === GENERATE ALL SIGNALS ===
        signals = []
        
        # 1. Order Book Signals
        book_signal = self.book_analyzer.get_latest_signal()
        if book_signal:
            signals.append(book_signal)
        
        # 2. Liquidity / FVG Signals
        self.fvg_detector.update(candles[-1])
        fvg_signal = self._check_fvg_entry(current_price, candles)
        if fvg_signal:
            signals.append(fvg_signal)
        
        # 3. Stop Hunt Signals
        hunt_signal = self.hunt_detector.update(candles[-1], candles)
        if hunt_signal:
            signals.append(hunt_signal)
        
        # 4. Judas Swing
        if self.session_analysis:
            judas = self.judas_detector.detect(
                candles=candles[-20:],
                session_info=self.session_analysis['session_info'],
                daily_bias=self.htf_bias,
                liquidity_pools=self.session_analysis['liquidity_pools']
            )
            if judas:
                signals.append({
                    'type': 'JUDAS_SWING',
                    'direction': 'LONG' if judas['type'] == 'BULLISH_JUDAS_SWING' else 'SHORT',
                    'strength': judas.get('confidence', 0.7),
                    'level': judas.get('entry_zone'),
                    'details': judas
                })
        
        # 5. Volume Delta Signals
        prices = [c.close for c in candles]
        cvd_values = self._get_cvd_series(candles)
        divergences = self.cvd_detector.detect(prices, cvd_values)
        for div in divergences:
            if div['strength'] >= self.config.min_signal_strength:
                signals.append({
                    'type': 'CVD_DIVERGENCE',
                    'direction': 'LONG' if div['type'] == 'BULLISH_DIVERGENCE' else 'SHORT',
                    'strength': div['strength'],
                    'details': div
                })
        
        # 6. Delta Exhaustion
        exhaustion = self._check_delta_exhaustion(candles)
        if exhaustion:
            signals.append(exhaustion)
        
        # 7. VWAP Extreme
        vwap_pos = self.vwap.get_price_position(current_price)
        if abs(vwap_pos['z_score']) >= 2.0:
            signals.append({
                'type': 'VWAP_EXTREME',
                'direction': 'SHORT' if vwap_pos['z_score'] > 0 else 'LONG',
                'strength': min(abs(vwap_pos['z_score']) / 3.0, 1.0),
                'level': self.vwap.vwap_value,
            })
        
        # === AGGREGATE SIGNALS ===
        kill_zone_active = self.kill_zone_mgr.should_trade(current_time)
        
        final_signal = self.signal_aggregator.aggregate(
            signals=signals,
            htf_bias=self.htf_bias,
            kill_zone=kill_zone_active
        )
        
        # === MAKE DECISION ===
        if final_signal:
            await self._handle_signal(final_signal, candles, current_price, current_time)
        
        # === MANAGE EXISTING POSITIONS ===
        await self._manage_positions(signals, candles, current_price, current_time)
    
    async def _handle_signal(self, signal: dict, candles: List, 
                              current_price: float, current_time: datetime):
        """Handle a validated trading signal — potentially open a position."""
        
        # Check if we can open a position
        risk_check = self.risk_mgr.can_open_position(
            strategy_type=signal['contributing_signals'][0]['type']
        )
        
        if not risk_check['allowed']:
            self.logger.info(f"Signal rejected: {risk_check['reason']}")
            return
        
        # Calculate trade parameters
        entry_price = signal.get('entry_level', current_price)
        atr = self._calc_atr(candles)
        
        # Stop loss (anti-hunt placement)
        stop_loss = self._calculate_stop_loss(
            direction=signal['direction'],
            entry=entry_price,
            candles=candles,
            atr=atr
        )
        
        # Take profit (liquidity target)
        take_profit = self._calculate_take_profit(
            direction=signal['direction'],
            entry=entry_price,
            stop=stop_loss,
            candles=candles
        )
        
        # Risk/Reward check
        if signal['direction'] == 'LONG':
            rr = (take_profit - entry_price) / (entry_price - stop_loss) if entry_price > stop_loss else 0
        else:
            rr = (entry_price - take_profit) / (stop_loss - entry_price) if stop_loss > entry_price else 0
        
        if rr < self.config.min_risk_reward:
            self.logger.info(f"Signal rejected: R:R {rr:.1f} < minimum {self.config.min_risk_reward}")
            return
        
        # Position sizing
        kz_mult = self.kill_zone_mgr.get_size_multiplier(current_time)
        
        size_info = self.position_sizer.calculate(
            equity=self.risk_mgr.account_equity,
            entry=entry_price,
            stop=stop_loss,
            pip_value=self._get_pip_value(),
            atr=atr,
            adv=self._get_adv(),
            signal_strength=signal['confluence_score']
        )
        
        if size_info['size'] <= 0:
            return
        
        # === EXECUTE ===
        order_type = 'LIMIT' if self.config.use_limit_orders and signal.get('entry_level') else 'MARKET'
        
        order = await self.executor.submit_order(
            symbol=self.config.symbol,
            side='BUY' if signal['direction'] == 'LONG' else 'SELL',
            size=size_info['size'],
            order_type=order_type,
            price=entry_price if order_type == 'LIMIT' else None,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timeout=self.config.order_timeout_seconds,
            metadata={
                'strategy': signal['contributing_signals'][0]['type'],
                'confluence_score': signal['confluence_score'],
                'htf_bias': self.htf_bias,
                'signal_count': signal['signal_count'],
                'risk_dollars': size_info['risk_dollars'],
                'risk_pct': size_info['risk_pct'],
                'risk_reward': rr,
            }
        )
        
        if order.status == 'FILLED':
            self.logger.info(
                f"POSITION OPENED: {signal['direction']} {self.config.symbol} "
                f"@ {order.fill_price}, Size: {size_info['size']}, "
                f"SL: {stop_loss}, TP: {take_profit}, R:R: {rr:.1f}"
            )
    
    async def _manage_positions(self, current_signals: List, candles: List,
                                 current_price: float, current_time: datetime):
        """Manage open positions — exits, trail stops, partial closes."""
        
        for position in self.risk_mgr.open_positions[:]:
            # Check standard exits
            exit_reason = None
            
            # Exit 1: Opposing high-confidence signal
            opposing = [
                s for s in current_signals
                if s['direction'] != position.direction and s.get('strength', 0) > 0.7
            ]
            if opposing:
                exit_reason = 'OPPOSING_SIGNAL'
            
            # Exit 2: Delta flip
            recent_cvd_slope = self._get_cvd_slope(lookback=10)
            if position.direction == 'LONG' and recent_cvd_slope < -0.5:
                exit_reason = 'DELTA_FLIP'
            elif position.direction == 'SHORT' and recent_cvd_slope > 0.5:
                exit_reason = 'DELTA_FLIP'
            
            # Exit 3: End of kill zone (if configured)
            if not self.kill_zone_mgr.should_trade(current_time):
                if position.holding_time_hours(current_time) > 2:
                    exit_reason = 'KILL_ZONE_END'
            
            # Exit 4: Spread blow-out
            spread_status = self.book_analyzer.get_spread_status()
            if spread_status.get('spread_ratio', 1) > 3.0:
                exit_reason = 'SPREAD_BLOWOUT'
            
            if exit_reason:
                await self.executor.close_position(position, reason=exit_reason)
                self.risk_mgr.close_position(position, current_price)
                self.logger.info(f"POSITION CLOSED: {exit_reason} @ {current_price}")
    
    async def _run_pre_session_analysis(self, data_feed, current_time):
        """Run pre-session analysis to set bias and map liquidity."""
        self.current_session_date = current_time.date()
        
        # Get HTF candles for bias
        htf_candles = self.candle_stores[self.config.htf_timeframe].get_candles()
        mtf_candles = self.candle_stores[self.config.mtf_timeframe].get_candles()
        
        # Determine HTF bias
        self.htf_bias = self._determine_htf_bias(htf_candles)
        
        # Map liquidity
        bsl = self.liquidity_mapper.detect_bsl(mtf_candles)
        ssl = self.liquidity_mapper.detect_ssl(mtf_candles)
        
        # Scan FVGs
        self.fvg_detector.scan(mtf_candles)
        
        # Store session analysis
        self.session_analysis = {
            'htf_bias': self.htf_bias,
            'bsl_pools': bsl,
            'ssl_pools': ssl,
            'liquidity_pools': bsl + ssl,
            'active_fvgs': self.fvg_detector.active_fvgs,
            'session_info': {
                'open_time': current_time.timestamp(),
                'open_price': mtf_candles[-1].close if mtf_candles else 0,
                'asian_high': self._get_asian_high(mtf_candles, current_time),
                'asian_low': self._get_asian_low(mtf_candles, current_time),
            }
        }
        
        self.logger.info(
            f"Pre-Session Analysis: Bias={self.htf_bias}, "
            f"BSL={len(bsl)} pools, SSL={len(ssl)} pools, "
            f"FVGs={len(self.fvg_detector.active_fvgs)}"
        )
    
    # === HELPER METHODS ===
    
    def _determine_htf_bias(self, candles: List) -> str:
        """Determine higher timeframe directional bias."""
        if len(candles) < 20:
            return 'NEUTRAL'
        
        # Simple market structure: higher highs + higher lows = bullish
        recent = candles[-20:]
        highs = [c.high for c in recent]
        lows = [c.low for c in recent]
        
        recent_high = max(highs[-5:])
        prev_high = max(highs[-10:-5])
        recent_low = min(lows[-5:])
        prev_low = min(lows[-10:-5])
        
        if recent_high > prev_high and recent_low > prev_low:
            return 'BULLISH'
        elif recent_high < prev_high and recent_low < prev_low:
            return 'BEARISH'
        return 'NEUTRAL'
    
    def _calculate_stop_loss(self, direction: str, entry: float, 
                              candles: List, atr: float) -> float:
        """Calculate anti-hunt stop loss placement."""
        buffer = 1.5 * atr
        
        if direction == 'LONG':
            # Find nearest SSL below entry
            recent_lows = sorted([c.low for c in candles[-20:]])
            nearest_low = recent_lows[0] if recent_lows else entry - 3 * atr
            return nearest_low - buffer
        else:
            recent_highs = sorted([c.high for c in candles[-20:]], reverse=True)
            nearest_high = recent_highs[0] if recent_highs else entry + 3 * atr
            return nearest_high + buffer
    
    def _calculate_take_profit(self, direction: str, entry: float, 
                                stop: float, candles: List) -> float:
        """Calculate take profit at next liquidity target."""
        sl_distance = abs(entry - stop)
        min_tp = entry + 2.5 * sl_distance if direction == 'LONG' else entry - 2.5 * sl_distance
        
        # Try to find a liquidity pool as target
        if self.session_analysis:
            if direction == 'LONG':
                targets = [p.price for p in self.session_analysis['bsl_pools'] if p.price > entry]
                return min(targets) if targets else min_tp
            else:
                targets = [p.price for p in self.session_analysis['ssl_pools'] if p.price < entry]
                return max(targets) if targets else min_tp
        
        return min_tp
    
    @staticmethod
    def _timeframe_to_seconds(tf: str) -> int:
        """Convert timeframe string to seconds."""
        multipliers = {'M': 60, 'H': 3600, 'D': 86400, 'W': 604800}
        value = int(tf[:-1])
        unit = tf[-1]
        return value * multipliers.get(unit, 60)
    
    async def stop(self):
        """Gracefully stop the trading system."""
        self.is_running = False
        self.logger.info("Stopping Order Flow Trading System")
    
    async def _emergency_shutdown(self):
        """Emergency shutdown — close all positions immediately."""
        self.logger.warning("EMERGENCY SHUTDOWN initiated")
        for position in self.risk_mgr.open_positions:
            await self.executor.close_position(position, reason='EMERGENCY')
        self.is_running = False
```

---

## 8. Latency Considerations: Crypto vs Forex

### 8.1 Latency Budget

```
TOTAL LATENCY BUDGET: 100ms (target)
═══════════════════════════════════════

Component           │ Crypto (CEX) │ Forex (Futures) │ Notes
────────────────────┼──────────────┼─────────────────┼──────────
Data Feed Latency   │  5-20ms      │  1-5ms          │ Exchange → System
Deserialization     │  1-2ms       │  1-2ms          │ JSON/FIX parsing
Feature Calculation │  2-5ms       │  2-5ms          │ Imbalance, delta
Signal Detection    │  3-10ms      │  3-10ms         │ Pattern matching
Aggregation         │  1-2ms       │  1-2ms          │ Score calculation
Risk Check          │  1-2ms       │  1-2ms          │ Position limits
Order Construction  │  1-2ms       │  1-2ms          │ Price, size, type
Order Submission    │  5-30ms      │  1-10ms         │ System → Exchange
────────────────────┼──────────────┼─────────────────┼──────────
TOTAL               │  20-75ms     │  12-40ms        │
────────────────────┼──────────────┼─────────────────┼──────────
FILL CONFIRMATION   │  +20-100ms   │  +5-50ms        │ Round-trip
```

### 8.2 Crypto-Specific Latency Factors

| Factor | Impact | Mitigation |
|--------|--------|-----------|
| WebSocket reconnection | 1-5s blind period | Redundant connections |
| Rate limits (Binance: 1200/min) | Request throttling | Batch updates, smart polling |
| Cross-exchange arbitrage latency | 50-200ms between exchanges | Co-locate with primary exchange |
| Blockchain confirmation | N/A for CEX trading | Only relevant for DEX |
| API overload during volatility | 100-5000ms degradation | Queue management, retry logic |

### 8.3 Forex-Specific Latency Factors

| Factor | Impact | Mitigation |
|--------|--------|-----------|
| Last look (LP rejection) | 200-2000ms delay or rejection | Use no-last-look venues |
| ECN bridge latency | 5-50ms | Direct market access (DMA) |
| Requotes | Order rejected, need resubmit | Use market orders or aggressive limits |
| Slippage during news | 5-50+ pips | Avoid trading 15min around news |
| Weekend gap | Cannot exit positions | Reduce exposure Friday PM |

### 8.4 Latency Optimization Strategies

```python
class LatencyOptimizer:
    """Strategies for minimizing end-to-end latency."""
    
    @staticmethod
    def pre_calculate_orders(signal_candidates: List[dict], 
                              risk_mgr: RiskManager) -> Dict[str, dict]:
        """
        Pre-calculate order parameters for likely signals.
        When a signal confirms, the order is ready to submit instantly.
        """
        pre_calculated = {}
        
        for signal in signal_candidates:
            if signal['probability'] > 0.5:  # Likely to trigger
                order_params = {
                    'direction': signal['direction'],
                    'size': risk_mgr.pre_calculate_size(signal),
                    'stop_loss': signal.get('stop_loss'),
                    'take_profit': signal.get('take_profit'),
                    'ready': True
                }
                pre_calculated[signal['id']] = order_params
        
        return pre_calculated
    
    @staticmethod
    def use_conditional_orders(executor, conditions: List[dict]):
        """
        Place conditional orders that execute at the exchange level
        without requiring round-trip to our system.
        
        Example: OCO (One-Cancels-Other) for SL and TP
        """
        for condition in conditions:
            executor.place_conditional(
                trigger_price=condition['trigger'],
                order_side=condition['side'],
                order_size=condition['size'],
                order_type='MARKET',  # Execute immediately when triggered
            )
```

---

## 9. System Architecture

### 9.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE                             │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Redis       │  │  TimescaleDB  │  │   Kafka       │       │
│  │  (State/Cache)│  │  (Historical) │  │  (Streaming)  │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
        │                     │                    │
        ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                             │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Data Ingestion │  │  Trading Engine   │  │  Monitoring   │  │
│  │  Service        │  │  (This Document)  │  │  Service      │  │
│  │                 │  │                   │  │               │  │
│  │  • WS Clients  │  │  • Signal Gen     │  │  • Metrics    │  │
│  │  • Normalizers  │  │  • Aggregation    │  │  • Alerts     │  │
│  │  • Publishers   │  │  • Risk Mgmt     │  │  • Dashboard  │  │
│  │                 │  │  • Execution      │  │               │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬───────┘  │
│           │                    │                     │           │
│           ▼                    ▼                     ▼           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              EXCHANGE CONNECTIVITY LAYER                     ││
│  │  • REST API Clients (order management)                      ││
│  │  • WebSocket Clients (market data)                          ││
│  │  • FIX Protocol (for institutional forex)                   ││
│  │  • Rate Limiting & Connection Management                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Deployment Models

| Model | Use Case | Infrastructure | Cost |
|-------|----------|---------------|------|
| **Single Process** | Development, paper trading | Local machine | Free |
| **Docker Compose** | Small-scale live trading | Single VPS | $20-100/mo |
| **Kubernetes** | Multi-symbol, multi-exchange | Cloud cluster | $200-1000/mo |
| **Co-located** | Latency-sensitive (HFT) | Exchange data center | $1000+/mo |

---

## 10. Backtesting Framework

### 10.1 Backtesting Architecture

```python
class OrderFlowBacktester:
    """
    Event-driven backtester for order flow strategies.
    Replays historical tick/L2 data through the trading system.
    """
    
    def __init__(self, config: SystemConfig, data_path: str):
        self.config = config
        self.data_path = data_path
        self.system = OrderFlowTradingSystem(config)
        self.results = BacktestResults()
    
    async def run(self, start_date: str, end_date: str):
        """Run backtest over specified date range."""
        data_feed = HistoricalDataFeed(
            path=self.data_path,
            start=start_date,
            end=end_date,
            symbol=self.config.symbol
        )
        
        # Replace executor with simulated executor
        self.system.executor = SimulatedExecutor(
            slippage_model='REALISTIC',
            fill_model='PARTIAL_FILL'
        )
        
        await self.system.start(data_feed)
        
        return self.results.compile()
    
    def get_metrics(self) -> dict:
        """Calculate comprehensive backtest metrics."""
        return {
            'total_trades': self.results.total_trades,
            'win_rate': self.results.win_rate,
            'profit_factor': self.results.profit_factor,
            'sharpe_ratio': self.results.sharpe_ratio,
            'sortino_ratio': self.results.sortino_ratio,
            'max_drawdown': self.results.max_drawdown,
            'avg_rr': self.results.avg_risk_reward,
            'expectancy': self.results.expectancy,
            'avg_holding_time': self.results.avg_holding_time,
            'best_kill_zone': self.results.best_kill_zone,
            'best_signal_type': self.results.best_signal_type,
        }
```

### 10.2 Key Backtesting Considerations

| Consideration | Importance | Implementation |
|---------------|-----------|----------------|
| **Realistic slippage** | Critical | Model based on historical spread + volume |
| **Partial fills** | Important | Simulate based on available liquidity |
| **Look-ahead bias** | Critical | Ensure no future data leaks into signals |
| **Survivorship bias** | Moderate | Include delisted pairs/tokens |
| **Regime changes** | Important | Test across multiple market conditions |
| **Transaction costs** | Important | Include spread + commission + swap |
| **Order book replay** | Ideal | Replay L2 data for book-based signals |

---

## 11. Monitoring & Alerting

### 11.1 Real-Time Monitoring Metrics

| Metric | Update Frequency | Alert Threshold |
|--------|-----------------|----------------|
| System latency (P99) | Per-event | >100ms |
| Data feed status | 1s | Disconnected >5s |
| Open P&L | Real-time | > -3% equity |
| Daily P&L | Per-trade | > -4% equity |
| Spread | Real-time | > 3x average |
| Signal generation rate | 1min | < 1 per hour or > 100 per hour |
| Fill rate | Per-order | < 80% |
| CPU/Memory usage | 10s | > 80% |

### 11.2 Alert Levels

| Level | Condition | Action |
|-------|-----------|--------|
| **INFO** | New signal generated, position opened | Log |
| **WARNING** | Spread widening, approaching daily limit | Reduce exposure |
| **CRITICAL** | Data feed lost, daily limit hit | Pause trading |
| **EMERGENCY** | System error, exchange outage | Close all positions |

---

## 12. Performance Metrics

### 12.1 Expected Performance Targets

| Metric | Conservative Target | Optimistic Target |
|--------|-------------------|-------------------|
| Annual Return | 15-25% | 30-50% |
| Max Drawdown | < 15% | < 10% |
| Sharpe Ratio | > 1.5 | > 2.5 |
| Win Rate | > 50% | > 60% |
| Average R:R | > 2.0 | > 3.0 |
| Profit Factor | > 1.5 | > 2.5 |
| Trades per Month | 20-40 | 15-30 |
| Avg Holding Time | 2-8 hours | 1-6 hours |

### 12.2 Performance Attribution

Track performance by:
- Signal type (which signals produce the best returns?)
- Kill zone (which session performs best?)
- Market condition (trending vs ranging)
- Day of week
- With/against HTF bias
- Confluence score range

---

## 13. Failure Modes & Recovery

### 13.1 Failure Scenarios

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Data feed disconnect | Heartbeat timeout | Reconnect, gap-fill, alert |
| Exchange API error | HTTP error code | Retry with backoff, failover |
| Incorrect fill | Position mismatch | Reconcile with exchange, adjust |
| System crash | Process monitor | Restart, reload state from DB |
| Strategy degradation | Drawdown threshold | Reduce size, pause, review |
| Flash crash | Extreme price move | Emergency exit, wait for stability |

### 13.2 Recovery Protocol

```python
async def recovery_protocol(system, failure_type: str):
    """Standard recovery protocol for system failures."""
    
    if failure_type == 'DATA_FEED_LOSS':
        # 1. Note time of last valid data
        # 2. Attempt reconnection (3 retries, exponential backoff)
        # 3. If reconnected: gap-fill missed data, recalculate state
        # 4. If not: switch to secondary feed or pause trading
        pass
    
    elif failure_type == 'EXCHANGE_ERROR':
        # 1. Log error details
        # 2. Check if positions are affected
        # 3. Reconcile position state with exchange
        # 4. Resume or escalate
        pass
    
    elif failure_type == 'SYSTEM_CRASH':
        # 1. Reload last known state from database
        # 2. Reconcile positions with exchange
        # 3. Check for missed signals/exits
        # 4. Resume in reduced-risk mode (50% size)
        pass
    
    elif failure_type == 'STRATEGY_DEGRADATION':
        # 1. Calculate recent performance metrics
        # 2. If drawdown > threshold: reduce position sizes by 50%
        # 3. If continued: pause for review period
        # 4. Analyze which signals are underperforming
        # 5. Consider parameter adjustment
        pass
```

---

## 14. Deployment Configuration

### 14.1 Environment Variables

```yaml
# config/production.yaml
system:
  name: "OrderFlowTrader"
  mode: "LIVE"  # LIVE, PAPER, BACKTEST
  
market:
  symbol: "EUR/USD"
  type: "FOREX"  # FOREX, CRYPTO
  exchange: "CME"  # CME, BINANCE, COINBASE

data:
  l2_feed: "cme_mdp3"
  trade_feed: "cme_mdp3"
  tick_data: true
  snapshot_interval_ms: 100

strategy:
  htf_timeframe: "1D"
  entry_timeframe: "1H"
  precision_timeframe: "15M"
  min_confluence: 0.55
  min_risk_reward: 2.0
  kill_zone_only: true

risk:
  risk_per_trade: 0.01
  max_daily_loss: 0.04
  max_weekly_loss: 0.08
  max_positions: 3
  max_correlated: 2

execution:
  order_type: "LIMIT"
  max_slippage_pips: 2.0
  timeout_seconds: 300
  
monitoring:
  log_level: "INFO"
  metrics_port: 9090
  alert_webhook: "${ALERT_WEBHOOK_URL}"
```

### 14.2 Multi-Symbol Configuration

```yaml
# config/multi_symbol.yaml
symbols:
  - name: "EUR/USD"
    type: "FOREX"
    risk_allocation: 0.30
    preferred_kill_zones: ["LONDON", "NEW_YORK"]
    
  - name: "GBP/USD"
    type: "FOREX"
    risk_allocation: 0.20
    preferred_kill_zones: ["LONDON"]
    
  - name: "BTC/USDT"
    type: "CRYPTO"
    risk_allocation: 0.25
    preferred_kill_zones: ["US_OPEN", "EUROPE_OPEN"]
    
  - name: "ETH/USDT"
    type: "CRYPTO"
    risk_allocation: 0.25
    preferred_kill_zones: ["US_OPEN", "EUROPE_OPEN"]

correlation_groups:
  - ["EUR/USD", "GBP/USD"]  # Cannot have max positions in both
  - ["BTC/USDT", "ETH/USDT"]  # Highly correlated
```

---

## 15. References

### System Design & Architecture

1. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. — Comprehensive system design for trading.

2. **Lopez de Prado, M. M.** (2018). *Advances in Financial Machine Learning*. Wiley. — Signal processing, backtesting methodology, position sizing.

3. **Chan, E. P.** (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. — Practical algorithmic trading implementation.

4. **Narang, R. K.** (2013). *Inside the Black Box: A Simple Guide to Quantitative and High-Frequency Trading*. Wiley.

### Order Flow & Market Microstructure

5. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell. — Theoretical foundation.

6. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — Measurement methodology.

7. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*.

8. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *RFS*.

### Risk Management

9. **Tharp, V. K.** (2006). *Trade Your Way to Financial Freedom*. McGraw-Hill. — Position sizing and expectancy.

10. **Vince, R.** (1992). *The Mathematics of Money Management*. Wiley. — Kelly criterion and optimal f.

### Implementation & Infrastructure

11. **Apache Kafka Documentation** — Streaming data architecture.
12. **TimescaleDB Documentation** — Time-series storage for financial data.
13. **Redis Documentation** — In-memory state management.
14. **Binance API Documentation** — WebSocket and REST API for crypto.
15. **CME Group** — "CME Globex MDP 3.0" — FX futures market data specification.

### ICT Methodology

16. **ICT (Inner Circle Trader)** — Complete methodology including kill zones, AMD model, liquidity concepts, Judas swing, and institutional order flow timing.

---

## Appendix A: Quick Reference — Signal Types and Parameters

| Signal Type | Min Strength | Default Weight | Min R:R | Typical Win Rate |
|------------|-------------|---------------|---------|-----------------|
| STOP_HUNT | 0.6 | 0.20 | 2.5:1 | 60-65% |
| CVD_DIVERGENCE | 0.5 | 0.18 | 2.0:1 | 55-62% |
| JUDAS_SWING | 0.6 | 0.15 | 3.0:1 | 58-65% |
| FVG_ENTRY | 0.5 | 0.12 | 2.0:1 | 55-60% |
| DELTA_EXHAUSTION | 0.7 | 0.10 | 2.0:1 | 55-60% |
| BOOK_IMBALANCE | 0.4 | 0.08 | 1.5:1 | 52-57% |
| ABSORPTION | 0.6 | 0.07 | 2.0:1 | 55-60% |
| VWAP_EXTREME | 0.5 | 0.05 | 1.5:1 | 55-60% |
| POC_TEST | 0.5 | 0.05 | 1.5:1 | 52-58% |

## Appendix B: Kill Zone Quick Reference

| Zone | UTC Start | UTC End | Day Rating | Position Mult |
|------|-----------|---------|------------|---------------|
| London | 02:00 | 05:00 | Tue-Thu best | 1.5x |
| NY | 07:00 | 10:00 | Tue-Thu best | 1.3x |
| London Close | 10:00 | 12:00 | All days | 1.0x |
| Asian | 00:00 | 04:00 | All days | 0.7x |
| Off-Hours | — | — | — | 0.0x (no trade) |

---

> **Previous Document**: [04_volume_delta_analysis.md](./04_volume_delta_analysis.md) — Volume Delta, CVD, VWAP, Volume Profile
> **Module Complete**: This concludes the Order Flow & Liquidity module (Module 03) of the trading strategies knowledge base.
