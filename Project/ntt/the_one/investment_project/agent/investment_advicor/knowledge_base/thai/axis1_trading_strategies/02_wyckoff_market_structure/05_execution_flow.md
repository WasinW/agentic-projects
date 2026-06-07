# ระบบเทรด Wyckoff — ขั้นตอนการดำเนินการแบบสมบูรณ์ (Complete Execution Flow)

> **โมดูล**: แกนที่ 1 — กลยุทธ์การเทรด
> **หัวข้อ**: 02 — วิธี Wyckoff และโครงสร้างตลาด
> **ไฟล์**: 05_execution_flow.md
> **เวอร์ชัน**: 1.0
> **อัปเดตล่าสุด**: 2026-04-12
> **ผู้เขียน**: ทีมฐานความรู้ — ระบบเทรด AI หลายเอเจนต์ NTT

---

## สารบัญ

1. [สถาปัตยกรรมระบบ](#1-สถาปั��ยกรรมระบบ)
2. [การออกแบบ State Machine](#2-การออกแบบ-state-machine)
3. [ตรรกะการสร้างสัญ��าณ](#3-ตรรก��การสร้างสัญญาณ)
4. [พารามิเตอร์ความเส��่ยง — ตารางสมบูรณ์](#4-พารามิเตอร์ความเสี่ยง--ตารางสมบูรณ์)
5. [อัลกอริทึมการกำหนดขนาดสถานะ](#5-อัลกอริทึมการกำหนดขนาดสถานะ)
6. [การจัดการคำสั่ง](#6-การจัดการคำสั่ง)
7. [การดำเนินการหลายกรอบเวลา](#7-การดำเนินการหลายกรอบเวลา)
8. [Pseudocode การนำไปใช้แบบสมบูรณ์](#8-pseudocode-การนำไปใ���้แบบสมบูรณ��)
9. [เมตริกประสิทธิภาพ](#9-เมตริกประสิทธิภาพ)
10. [การจัดการข้อผิดพลาดและกรณีพิเศษ](#10-การ���ัดการ��้อผิดพล���ดและกรณีพิเศษ)
11. [กรอบการทดสอบย้อนหลัง (Backtesting)](#11-กรอบการทดสอ��ย้อนหลัง-backtesting)
12. [การนำไปใช้งานจริง (Production)](#12-การนำไปใช้งานจริง-production)
13. [เอกสารอ้างอิง](#13-เอกสาร���้างอิง)

---

## 1. สถาปัตยกรรมระบบ (System Architecture)

### 1.1 แผนผังสถาปัตยกรรมระดับสูง

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WYCKOFF TRADING SYSTEM ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌──────────────────────────────────────────────┐   │
│  │ DATA LAYER  │    │            ANALYSIS LAYER                    │   │
│  │             │    │                                              │   │
│  │ Market Data ├───→│ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │   │
│  │ (OHLCV)    │    │ │ Indicator │ │  Swing   │ │   Volume     │ │   │
│  │             │    │ │  Engine  │ │ Detector │ │  Analyzer    │ │   │
│  │ Tick Data   │    │ └────┬─────┘ └────┬─────┘ └──────┬───────┘ │   │
│  │             │    │      │            │               │         │   │
│  │ Order Book  │    │      ▼            ▼               ▼         │   │
│  │             │    │ ┌─────────────────────────────────────────┐ │   │
│  │ On-Chain    │    │ │         WYCKOFF PHASE DETECTOR          │ │   │
│  │ (Crypto)   │    │ │  (State Machine — identifies current    │ │   │
│  │             │    │ │   phase and sub-events)                 │ │   │
│  └─────────────┘    │ └──────────────────┬──────────────────────┘ │   │
│                     │                    │                         │   │
│                     │      ▼             ▼            ▼            │   │
│                     │ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │   │
│                     │ │ Market   │ │   VSA    │ │   MTF        │ │   │
│                     │ │Structure │ │ Scanner  │ │  Confluence  │ │   │
│                     │ │ (BoS/    │ │          │ │  Analyzer    │ │   │
│                     │ │  ChoCh)  │ │          │ │              │ │   │
│                     │ └────┬─────┘ └────┬─────┘ └──────┬───────┘ │   │
│                     │      │            │               │         │   │
│                     └──────┼────────────┼───────────────┼─────────┘   │
│                            │            │               │             │
│                            ▼            ▼               ▼             │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                   SIGNAL GENERATION LAYER                        │ │
│  │                                                                  │ │
│  │  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐ │ │
│  │  │ Signal Combiner  │   │ Confidence Score  │   │  Filter &    │ │ │
│  │  │ (Wyckoff + Struct│   │ Calculator       │   │  Validator   │ │ │
│  │  │ + VSA + MTF)    │   │                  │   │              │ │ │
│  │  └────────┬────────┘   └────────┬─────────┘   └──────┬───────┘ │ │
│  │           │                     │                     │         │ │
│  └───────────┼─────────────────────┼─────────────────────┼─────────┘ │
│              │                     │                     │           │
│              ▼                     ▼                     ▼           │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                   EXECUTION LAYER                                │ │
│  │                                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │ │
│  │  │Risk Manager  │  │Position Sizer │  │ Order Manager         │ │ │
│  │  │              │  │              │  │ (Entry/Exit/Trail)    │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘ │ │
│  │         │                 │                       │             │ │
│  │         ▼                 ▼                       ▼             │ │
│  │  ┌─────────────────────────────────────────────────────────────┐│ │
│  │  │              BROKER / EXCHANGE API                          ││ │
│  │  └─────────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 ความรับผิดชอบของส่วนประกอบ

| Component | Responsibility | Input | Output |
|---|---|---|---|
| **Data Layer** | Collect and normalize market data | Raw feeds | Clean OHLCV + metadata |
| **Indicator Engine** | Calculate ATR, EMA, volume averages | OHLCV | Technical indicators |
| **Swing Detector** | Identify swing highs and lows | OHLCV + ATR | Swing points + classification |
| **Volume Analyzer** | Volume normalization, CVD, Weis waves | OHLCV | Volume metrics |
| **Wyckoff Phase Detector** | State machine for phase identification | All indicators | Current phase + events |
| **Market Structure** | BoS/ChoCh detection | Swing points | Structure events |
| **VSA Scanner** | Volume-spread-close pattern detection | OHLCV + context | VSA signals |
| **MTF Confluence** | Multi-timeframe agreement | Per-TF states | Directional bias + confidence |
| **Signal Generator** | Combine all analysis into trade signals | All analysis outputs | Trade signals |
| **Risk Manager** | Validate signals against risk rules | Signals + account state | Approved/rejected signals |
| **Position Sizer** | Calculate appropriate position size | Signal + risk params | Lot size |
| **Order Manager** | Execute and manage orders | Sized signals | Filled orders |

---

## 2. การออกแบบ State Machine

### 2.1 State Machine หลัก

```python
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict

class MarketPhase(Enum):
    UNKNOWN = auto()
    ACCUMULATION_A = auto()  # Stopping the downtrend
    ACCUMULATION_B = auto()  # Building cause
    ACCUMULATION_C = auto()  # Spring/Test
    ACCUMULATION_D = auto()  # SOS/LPS
    ACCUMULATION_E = auto()  # Markup begins
    MARKUP = auto()
    RE_ACCUMULATION = auto()
    DISTRIBUTION_A = auto()  # Stopping the uptrend
    DISTRIBUTION_B = auto()  # Building cause
    DISTRIBUTION_C = auto()  # UTAD/Test
    DISTRIBUTION_D = auto()  # SOW/LPSY
    DISTRIBUTION_E = auto()  # Markdown begins
    MARKDOWN = auto()
    RE_DISTRIBUTION = auto()

class StructureState(Enum):
    BULLISH = auto()
    BEARISH = auto()
    RANGING = auto()
    TRANSITIONING = auto()
    UNKNOWN = auto()

@dataclass
class SystemState:
    """Complete system state at any point in time."""
    # Phase tracking
    market_phase: MarketPhase = MarketPhase.UNKNOWN
    phase_confidence: float = 0.0
    phase_start_bar: int = 0
    phase_duration: int = 0
    
    # Structure tracking
    structure_state: StructureState = StructureState.UNKNOWN
    structure_confidence: float = 0.0
    last_bos: Optional[Dict] = None
    last_choch: Optional[Dict] = None
    
    # Key levels
    ice_level: float = 0.0          # Resistance in accumulation / Support in distribution
    creek_level: float = 0.0        # Support in accumulation / Resistance in distribution
    range_height: float = 0.0
    
    # Events detected
    events_detected: List[Dict] = field(default_factory=list)
    
    # VSA state
    last_vsa_signal: Optional[Dict] = None
    cvd: float = 0.0
    sdpi: float = 1.0
    
    # MTF
    mtf_bias: str = 'NEUTRAL'
    mtf_confidence: float = 0.0
    
    # Trading state
    active_positions: List[Dict] = field(default_factory=list)
    pending_orders: List[Dict] = field(default_factory=list)
    daily_pnl: float = 0.0
    daily_trades: int = 0
```

### 2.2 กฎการเปลี่ยนเฟส

```python
class PhaseTransitionEngine:
    """
    Manages transitions between Wyckoff phases based on detected events.
    """
    
    VALID_TRANSITIONS = {
        MarketPhase.UNKNOWN: [
            MarketPhase.ACCUMULATION_A,
            MarketPhase.DISTRIBUTION_A,
            MarketPhase.MARKUP,
            MarketPhase.MARKDOWN,
        ],
        MarketPhase.MARKDOWN: [
            MarketPhase.ACCUMULATION_A,
            MarketPhase.RE_DISTRIBUTION,
        ],
        MarketPhase.ACCUMULATION_A: [
            MarketPhase.ACCUMULATION_B,
            MarketPhase.MARKDOWN,  # Failed — continues down
        ],
        MarketPhase.ACCUMULATION_B: [
            MarketPhase.ACCUMULATION_C,
            MarketPhase.ACCUMULATION_D,  # Skip C (no spring, direct SOS)
            MarketPhase.MARKDOWN,  # Failed
        ],
        MarketPhase.ACCUMULATION_C: [
            MarketPhase.ACCUMULATION_D,
            MarketPhase.ACCUMULATION_B,  # Spring failed, back to B
        ],
        MarketPhase.ACCUMULATION_D: [
            MarketPhase.ACCUMULATION_E,
            MarketPhase.ACCUMULATION_B,  # SOS failed, back to range
        ],
        MarketPhase.ACCUMULATION_E: [
            MarketPhase.MARKUP,
        ],
        MarketPhase.MARKUP: [
            MarketPhase.DISTRIBUTION_A,
            MarketPhase.RE_ACCUMULATION,
        ],
        MarketPhase.RE_ACCUMULATION: [
            MarketPhase.MARKUP,
            MarketPhase.DISTRIBUTION_A,  # Failed re-accumulation
        ],
        MarketPhase.DISTRIBUTION_A: [
            MarketPhase.DISTRIBUTION_B,
            MarketPhase.MARKUP,  # Failed — continues up
        ],
        MarketPhase.DISTRIBUTION_B: [
            MarketPhase.DISTRIBUTION_C,
            MarketPhase.DISTRIBUTION_D,  # Skip C (no UTAD, direct SOW)
            MarketPhase.MARKUP,  # Failed
        ],
        MarketPhase.DISTRIBUTION_C: [
            MarketPhase.DISTRIBUTION_D,
            MarketPhase.DISTRIBUTION_B,  # UTAD failed (genuine breakout)
        ],
        MarketPhase.DISTRIBUTION_D: [
            MarketPhase.DISTRIBUTION_E,
            MarketPhase.DISTRIBUTION_B,  # SOW failed, back to range
        ],
        MarketPhase.DISTRIBUTION_E: [
            MarketPhase.MARKDOWN,
        ],
        MarketPhase.RE_DISTRIBUTION: [
            MarketPhase.MARKDOWN,
            MarketPhase.ACCUMULATION_A,  # Failed re-distribution
        ],
    }
    
    TRANSITION_TRIGGERS = {
        (MarketPhase.MARKDOWN, MarketPhase.ACCUMULATION_A): {
            'events': ['PS'],
            'conditions': lambda s: s.structure_state == StructureState.BEARISH
        },
        (MarketPhase.ACCUMULATION_A, MarketPhase.ACCUMULATION_B): {
            'events': ['SC', 'AR', 'ST'],
            'conditions': lambda s: len([e for e in s.events_detected 
                                        if e['event'] in ['SC', 'AR']]) >= 2
        },
        (MarketPhase.ACCUMULATION_B, MarketPhase.ACCUMULATION_C): {
            'events': ['SPRING'],
            'conditions': lambda s: any(e['event'] == 'SPRING' for e in s.events_detected)
        },
        (MarketPhase.ACCUMULATION_C, MarketPhase.ACCUMULATION_D): {
            'events': ['TEST_OF_SPRING', 'SOS'],
            'conditions': lambda s: any(e['event'] in ['TEST_OF_SPRING', 'SOS'] 
                                       for e in s.events_detected)
        },
        (MarketPhase.ACCUMULATION_D, MarketPhase.ACCUMULATION_E): {
            'events': ['LPS', 'BU'],
            'conditions': lambda s: s.phase_confidence > 0.85
        },
    }
    
    def attempt_transition(self, current_state, new_event):
        """
        Attempt a phase transition based on a new event.
        
        Returns:
            tuple: (new_phase, confidence) or (None, 0) if no transition
        """
        current_phase = current_state.market_phase
        valid_next = self.VALID_TRANSITIONS.get(current_phase, [])
        
        for next_phase in valid_next:
            trigger_key = (current_phase, next_phase)
            trigger = self.TRANSITION_TRIGGERS.get(trigger_key)
            
            if trigger:
                event_match = new_event['event'] in trigger['events']
                condition_met = trigger['conditions'](current_state)
                
                if event_match and condition_met:
                    # Calculate transition confidence
                    confidence = self._calculate_transition_confidence(
                        current_state, next_phase, new_event
                    )
                    return next_phase, confidence
        
        return None, 0.0
    
    def _calculate_transition_confidence(self, state, new_phase, event):
        """Calculate confidence for the proposed transition."""
        base_confidence = event.get('confidence', 0.5)
        
        # Boost for VSA confirmation
        if state.last_vsa_signal and state.last_vsa_signal['bias'] != 'NEUTRAL':
            base_confidence += 0.05
        
        # Boost for MTF alignment
        if state.mtf_confidence > 0.5:
            base_confidence += 0.10
        
        # Boost for structure confirmation
        if state.structure_confidence > 0.7:
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
```

### 2.3 แผนผัง State Machine (แบบย่อ)

```
                    ┌────────────────────┐
                    │      UNKNOWN       │
                    └──────┬───────┬─────┘
                           │       │
              ┌────────────┘       └────────────┐
              ▼                                 ▼
    ┌─────────────────┐               ┌─────────────────┐
    │   MARKDOWN      │◄──────────────│   DISTRIBUTION  │
    │   (LH + LL)     │               │   (A→B→C→D→E)  │
    └────────┬────────┘               └────────▲────────┘
             │                                 │
             │ SC detected                     │ BC detected
             ▼                                 │
    ┌─────────────────┐               ┌────────┴────────┐
    │  ACCUMULATION   │               │     MARKUP      │
    │  (A→B→C→D→E)   │──────────────→│   (HH + HL)    │
    └─────────────────┘  SOS+LPS     └─────────────────┘
             │               confirmed         ▲
             │                                 │
             │    ┌────────────────┐           │
             └───→│RE-ACCUMULATION │───────────┘
                  │(stepping stone)│   Breakout
                  └────────────────┘
```

---

## 3. ตรรกะการสร้างสัญญาณ (Signal Generation Logic)

### 3.1 ท่อสร้างสัญญาณ (Signal Generation Pipeline)

```python
class SignalGenerator:
    """
    Generates trade signals by combining Wyckoff, Structure, VSA, and MTF analysis.
    """
    
    def __init__(self, config):
        self.config = config
        self.min_confidence = config.get('min_confidence', 0.65)
        self.min_rr = config.get('min_risk_reward', 2.0)
        
    def generate_signals(self, state: SystemState, candle: Dict, atr: float) -> List[Dict]:
        """
        Generate trade signals from current system state.
        
        Signals are generated when multiple analysis components agree.
        """
        signals = []
        
        # ====== LONG SIGNALS ======
        
        # Signal 1: Spring Entry (Highest priority long)
        if self._spring_entry_conditions(state, candle, atr):
            signals.append(self._create_spring_signal(state, candle, atr))
        
        # Signal 2: Test of Spring Entry
        if self._test_of_spring_conditions(state, candle, atr):
            signals.append(self._create_test_of_spring_signal(state, candle, atr))
        
        # Signal 3: SOS Breakout Entry
        if self._sos_breakout_conditions(state, candle, atr):
            signals.append(self._create_sos_signal(state, candle, atr))
        
        # Signal 4: LPS Pullback Entry
        if self._lps_conditions(state, candle, atr):
            signals.append(self._create_lps_signal(state, candle, atr))
        
        # Signal 5: Markup Pullback Entry
        if self._markup_pullback_conditions(state, candle, atr):
            signals.append(self._create_markup_pullback_signal(state, candle, atr))
        
        # Signal 6: Bullish ChoCh Entry
        if self._bullish_choch_conditions(state, candle, atr):
            signals.append(self._create_choch_long_signal(state, candle, atr))
        
        # ====== SHORT SIGNALS ======
        
        # Signal 7: UTAD Entry (Highest priority short)
        if self._utad_entry_conditions(state, candle, atr):
            signals.append(self._create_utad_signal(state, candle, atr))
        
        # Signal 8: Test of UTAD Entry
        if self._test_of_utad_conditions(state, candle, atr):
            signals.append(self._create_test_of_utad_signal(state, candle, atr))
        
        # Signal 9: SOW Breakdown Entry
        if self._sow_breakdown_conditions(state, candle, atr):
            signals.append(self._create_sow_signal(state, candle, atr))
        
        # Signal 10: LPSY Entry
        if self._lpsy_conditions(state, candle, atr):
            signals.append(self._create_lpsy_signal(state, candle, atr))
        
        # Signal 11: Markdown Rally Sell
        if self._markdown_rally_conditions(state, candle, atr):
            signals.append(self._create_markdown_rally_signal(state, candle, atr))
        
        # Signal 12: Bearish ChoCh Entry
        if self._bearish_choch_conditions(state, candle, atr):
            signals.append(self._create_choch_short_signal(state, candle, atr))
        
        # ====== FILTER ======
        
        # Remove signals below confidence threshold
        signals = [s for s in signals if s['confidence'] >= self.min_confidence]
        
        # Remove signals below minimum R:R
        signals = [s for s in signals if s.get('risk_reward', 0) >= self.min_rr]
        
        # Sort by confidence (best first)
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Limit to top N signals per bar
        max_signals = self.config.get('max_signals_per_bar', 2)
        signals = signals[:max_signals]
        
        return signals
    
    def _spring_entry_conditions(self, state, candle, atr):
        """Check if Spring entry conditions are met."""
        return (
            state.market_phase == MarketPhase.ACCUMULATION_C and
            any(e['event'] == 'SPRING' and e.get('spring_type', 0) >= 2 
                for e in state.events_detected[-5:]) and
            state.phase_confidence >= 0.70 and
            state.mtf_bias in ['NEUTRAL', 'BULLISH', 'STRONG_BULLISH'] and
            len(state.active_positions) < self.config.get('max_positions', 3)
        )
    
    def _create_spring_signal(self, state, candle, atr):
        """Create Spring entry signal."""
        spring_event = next(e for e in reversed(state.events_detected) 
                          if e['event'] == 'SPRING')
        
        entry = candle['close']
        stop_loss = spring_event['price_low'] - atr * 0.5
        risk = entry - stop_loss
        target_1 = entry + state.range_height
        target_2 = entry + state.range_height * 1.618
        
        confidence = spring_event['confidence']
        # Boost for VSA confirmation
        if state.last_vsa_signal and state.last_vsa_signal['bias'] == 'BULLISH':
            confidence = min(0.95, confidence + 0.10)
        # Boost for MTF alignment
        if state.mtf_bias in ['BULLISH', 'STRONG_BULLISH']:
            confidence = min(0.95, confidence + 0.05)
        
        return {
            'signal_type': 'SPRING_ENTRY',
            'direction': 'LONG',
            'entry_price': entry,
            'stop_loss': stop_loss,
            'target_1': target_1,
            'target_2': target_2,
            'risk': risk,
            'risk_reward': (target_1 - entry) / risk if risk > 0 else 0,
            'confidence': confidence,
            'phase': state.market_phase.name,
            'position_pct': 0.30,  # 30% of planned total position
            'max_risk_pct': 2.0,
            'trigger_event': 'SPRING',
            'notes': f"Spring Type {spring_event.get('spring_type')} at {spring_event['price_low']:.5f}"
        }
    
    # ... similar methods for other signal types ...
```

### 3.2 กฎการตรวจสอบสัญญาณ

```python
class SignalValidator:
    """
    Validates generated signals against risk rules and market conditions.
    """
    
    def validate(self, signal, state, account):
        """
        Validate a signal before execution.
        
        Returns:
            tuple: (is_valid: bool, reason: str)
        """
        checks = []
        
        # Check 1: Account risk limit
        risk_amount = account.balance * signal['max_risk_pct'] / 100
        if account.daily_drawdown + risk_amount > account.max_daily_loss:
            checks.append((False, 'Would exceed daily loss limit'))
        else:
            checks.append((True, 'Daily risk OK'))
        
        # Check 2: Correlation with existing positions
        for pos in state.active_positions:
            if pos['symbol'] == signal.get('symbol') and pos['direction'] == signal['direction']:
                if len([p for p in state.active_positions 
                       if p['direction'] == signal['direction']]) >= 3:
                    checks.append((False, 'Too many same-direction positions'))
                    break
        else:
            checks.append((True, 'Correlation OK'))
        
        # Check 3: Time-based filters
        if self._is_high_impact_news_period():
            checks.append((False, 'High-impact news within 30 minutes'))
        else:
            checks.append((True, 'No imminent news'))
        
        # Check 4: Minimum R:R after slippage estimate
        estimated_slippage = signal.get('estimated_slippage', 0)
        adjusted_rr = (signal['target_1'] - signal['entry_price'] - estimated_slippage) / \
                     (signal['risk'] + estimated_slippage)
        if adjusted_rr < 1.5:
            checks.append((False, f'Adjusted R:R too low: {adjusted_rr:.2f}'))
        else:
            checks.append((True, f'Adjusted R:R OK: {adjusted_rr:.2f}'))
        
        # Check 5: Spread/liquidity
        if signal.get('current_spread', 0) > signal['risk'] * 0.1:
            checks.append((False, 'Spread too wide relative to stop distance'))
        else:
            checks.append((True, 'Spread acceptable'))
        
        # Overall validation
        all_valid = all(c[0] for c in checks)
        reasons = [c[1] for c in checks if not c[0]]
        
        return all_valid, '; '.join(reasons) if reasons else 'All checks passed'
```

---

## 4. พารามิเตอร์ความเสี่ยง — ตารางสมบูรณ์

### 4.1 ตารางพารามิเตอร์ความเสี่ยงหลัก

| Signal Type | Phase | Direction | Risk % | SL (ATR) | TP1 (ATR) | TP2 (ATR) | TP3 (ATR) | Min R:R | Max Pos | Confidence Min |
|---|---|---|---|---|---|---|---|---|---|---|
| Spring (Type 3) | Accum C | Long | 2.0% | 0.5–1.0 | 2.0 | 3.5 | 5.0 | 3:1 | 30% | 0.80 |
| Spring (Type 2) | Accum C | Long | 1.5% | 1.0–1.5 | 2.0 | 3.0 | 4.5 | 2.5:1 | 25% | 0.70 |
| Test of Spring | Accum C | Long | 2.0% | 0.5–0.8 | 2.0 | 3.5 | 5.0 | 3.5:1 | 30% | 0.85 |
| SOS Breakout | Accum D | Long | 1.5% | 1.5–2.0 | 2.0 | 3.0 | 4.0 | 2:1 | 25% | 0.70 |
| LPS | Accum D | Long | 1.5% | 0.5–1.0 | 1.5 | 3.0 | 4.5 | 2.5:1 | 20% | 0.75 |
| Back-Up (BU) | Accum E | Long | 1.0% | 0.3–0.8 | 1.5 | 2.5 | 4.0 | 2:1 | 15% | 0.80 |
| Markup Pullback | Markup | Long | 1.0% | 1.0–1.5 | 1.5 | 2.5 | 3.5 | 2:1 | 20% | 0.65 |
| Bullish ChoCh | Transition | Long | 1.5% | 1.0–2.0 | 2.0 | 3.5 | 5.0 | 2.5:1 | 20% | 0.70 |
| Bullish BoS PB | Markup | Long | 1.0% | 1.0–1.5 | 1.5 | 2.5 | 3.5 | 2:1 | 20% | 0.65 |
| UTAD (Type 3) | Dist C | Short | 2.0% | 0.5–1.0 | 2.0 | 3.5 | 5.0 | 3:1 | 30% | 0.80 |
| UTAD (Type 2) | Dist C | Short | 1.5% | 1.0–1.5 | 2.0 | 3.0 | 4.5 | 2.5:1 | 25% | 0.70 |
| Test of UTAD | Dist C | Short | 2.0% | 0.5–0.8 | 2.0 | 3.5 | 5.0 | 3.5:1 | 30% | 0.85 |
| SOW Breakdown | Dist D | Short | 1.5% | 1.5–2.0 | 2.0 | 3.0 | 4.0 | 2:1 | 25% | 0.70 |
| LPSY | Dist D | Short | 1.5% | 0.5–1.0 | 1.5 | 3.0 | 4.5 | 2.5:1 | 20% | 0.75 |
| SOW Retest | Dist E | Short | 1.0% | 0.5–0.8 | 1.5 | 2.5 | 4.0 | 2.5:1 | 15% | 0.80 |
| Markdown Rally | Markdown | Short | 1.0% | 1.0–1.5 | 1.5 | 2.5 | 3.5 | 2:1 | 20% | 0.65 |
| Bearish ChoCh | Transition | Short | 1.5% | 1.0–2.0 | 2.0 | 3.5 | 5.0 | 2.5:1 | 20% | 0.70 |
| Bearish BoS PB | Markdown | Short | 1.0% | 1.0–1.5 | 1.5 | 2.5 | 3.5 | 2:1 | 20% | 0.65 |

### 4.2 การปรับขนาดความเสี่ยงตามความเชื่อมั่นเฟส

$$
R_{\text{actual}} = R_{\text{max}} \times \min\left(1.0, \frac{C_{\text{phase}} - C_{\text{min}}}{1.0 - C_{\text{min}}}\right)
$$

| Phase Confidence | Risk Multiplier | Position Size |
|---|---|---|
| 0.90–1.00 | 1.00x | Full |
| 0.80–0.89 | 0.85x | 85% |
| 0.70–0.79 | 0.70x | 70% |
| 0.65–0.69 | 0.50x | 50% |
| < 0.65 | 0.00x | No trade |

### 4.3 ขีดจำกัดความเสี่ยงระดับบัญชี

| Limit Type | Value | Action When Exceeded |
|---|---|---|
| Max risk per trade | 2.0% of equity | Reject signal |
| Max daily loss | 4.0% of equity | Stop trading for the day |
| Max weekly loss | 6.0% of equity | Reduce all sizes by 50% |
| Max monthly loss | 10.0% of equity | Stop trading, review |
| Max drawdown | 15.0% of peak equity | Full system shutdown |
| Max open positions | 5 | Reject new signals |
| Max correlated positions | 3 same direction | Reject correlated signal |
| Max per-instrument risk | 3.0% of equity | Spread across instruments |

---

## 5. อัลกอริทึมการกำหนดขนาดสถานะ (Position Sizing)

### 5.1 สูตรการกำหนดขนาดสถานะหลัก

```python
class PositionSizer:
    """
    Calculate position size based on signal parameters and account state.
    """
    
    def calculate_size(self, signal, account, market_info):
        """
        Calculate the appropriate position size.
        
        Parameters:
            signal: dict with entry_price, stop_loss, max_risk_pct, confidence
            account: dict with balance, equity, margin_used, daily_loss
            market_info: dict with pip_value, min_lot, max_lot, lot_step
        
        Returns:
            dict with lot_size, risk_amount, margin_required
        """
        # Step 1: Determine risk amount
        risk_pct = signal['max_risk_pct'] / 100.0
        
        # Apply confidence scaling
        confidence_factor = min(1.0, 
            (signal['confidence'] - 0.60) / (1.0 - 0.60))  # Scale from 0.60 to 1.0
        risk_pct *= confidence_factor
        
        # Apply drawdown scaling (reduce risk when in drawdown)
        drawdown_pct = 1 - (account['equity'] / account.get('peak_equity', account['equity']))
        if drawdown_pct > 0.05:
            dd_factor = max(0.25, 1.0 - drawdown_pct * 2)
            risk_pct *= dd_factor
        
        risk_amount = account['equity'] * risk_pct
        
        # Step 2: Calculate stop distance
        if signal['direction'] == 'LONG':
            stop_distance = signal['entry_price'] - signal['stop_loss']
        else:
            stop_distance = signal['stop_loss'] - signal['entry_price']
        
        if stop_distance <= 0:
            return {'lot_size': 0, 'error': 'Invalid stop distance'}
        
        # Step 3: Calculate position size
        pip_value = market_info['pip_value']  # Value per pip per standard lot
        stop_pips = stop_distance / market_info['pip_size']
        
        # Position size = Risk Amount / (Stop Pips * Pip Value)
        lots = risk_amount / (stop_pips * pip_value)
        
        # Step 4: Apply constraints
        lots = max(market_info['min_lot'], lots)
        lots = min(market_info['max_lot'], lots)
        
        # Round to lot step
        lot_step = market_info['lot_step']
        lots = round(lots / lot_step) * lot_step
        
        # Step 5: Check margin
        margin_required = lots * market_info['margin_per_lot']
        available_margin = account['equity'] - account['margin_used']
        
        if margin_required > available_margin * 0.8:  # Use max 80% of available margin
            lots = (available_margin * 0.8) / market_info['margin_per_lot']
            lots = round(lots / lot_step) * lot_step
        
        # Step 6: Final risk calculation
        actual_risk = lots * stop_pips * pip_value
        actual_risk_pct = actual_risk / account['equity'] * 100
        
        return {
            'lot_size': lots,
            'risk_amount': actual_risk,
            'risk_pct': actual_risk_pct,
            'stop_pips': stop_pips,
            'margin_required': lots * market_info['margin_per_lot'],
            'confidence_factor': confidence_factor,
            'drawdown_factor': dd_factor if drawdown_pct > 0.05 else 1.0,
        }
```

### 5.2 การปรับใช้ Kelly Criterion

For optimal growth, apply a fractional Kelly criterion:

$$
f^* = \frac{p \cdot b - q}{b}
$$

Where:
- $f^*$ = optimal fraction of capital to risk
- $p$ = probability of winning (from confidence score)
- $q = 1 - p$ = probability of losing
- $b$ = win/loss ratio (risk/reward)

Apply half-Kelly for safety:

$$
f_{\text{actual}} = 0.5 \times f^*
$$

```python
def kelly_position_size(win_rate, avg_win, avg_loss, equity):
    """
    Calculate position size using half-Kelly criterion.
    """
    if avg_loss == 0:
        return 0
    
    b = avg_win / avg_loss  # Win/loss ratio
    p = win_rate
    q = 1 - p
    
    kelly = (p * b - q) / b
    half_kelly = max(0, kelly * 0.5)
    
    # Cap at maximum risk
    position_risk = min(half_kelly, 0.02)  # Max 2%
    
    return position_risk * equity
```

---

## 6. การจัดการคำสั่ง (Order Management)

### 6.1 ประเภทคำสั่งและการดำเนินการ

```python
class OrderManager:
    """
    Manages order placement, modification, and cancellation.
    """
    
    def __init__(self, broker_api, config):
        self.broker = broker_api
        self.config = config
        self.open_orders = []
        self.filled_orders = []
    
    def place_entry_order(self, signal, position_size):
        """
        Place entry order based on signal type.
        """
        order_type = self._determine_order_type(signal)
        
        if order_type == 'MARKET':
            # Immediate execution for high-confidence signals
            order = {
                'type': 'MARKET',
                'symbol': signal.get('symbol'),
                'direction': signal['direction'],
                'size': position_size['lot_size'],
                'stop_loss': signal['stop_loss'],
                'take_profit_1': signal['target_1'],
                'take_profit_2': signal.get('target_2'),
            }
        
        elif order_type == 'LIMIT':
            # Better price entry for pullback trades
            if signal['direction'] == 'LONG':
                limit_price = signal['entry_price'] - signal.get('limit_offset', 0)
            else:
                limit_price = signal['entry_price'] + signal.get('limit_offset', 0)
            
            order = {
                'type': 'LIMIT',
                'symbol': signal.get('symbol'),
                'direction': signal['direction'],
                'size': position_size['lot_size'],
                'price': limit_price,
                'stop_loss': signal['stop_loss'],
                'take_profit_1': signal['target_1'],
                'expiry': self._calculate_expiry(signal),
            }
        
        elif order_type == 'STOP':
            # Breakout entry
            if signal['direction'] == 'LONG':
                stop_price = signal['entry_price']  # Buy above level
            else:
                stop_price = signal['entry_price']  # Sell below level
            
            order = {
                'type': 'STOP',
                'symbol': signal.get('symbol'),
                'direction': signal['direction'],
                'size': position_size['lot_size'],
                'price': stop_price,
                'stop_loss': signal['stop_loss'],
                'take_profit_1': signal['target_1'],
                'expiry': self._calculate_expiry(signal),
            }
        
        # Submit order
        result = self.broker.submit_order(order)
        
        if result['status'] == 'FILLED' or result['status'] == 'PENDING':
            self.open_orders.append({**order, **result})
        
        return result
    
    def manage_position(self, position, candle, state, atr):
        """
        Manage an open position — check for exits, trail stops, scale.
        """
        actions = []
        
        # Check TP1 hit
        if not position.get('tp1_hit'):
            if position['direction'] == 'LONG' and candle['high'] >= position['take_profit_1']:
                actions.append({
                    'action': 'PARTIAL_CLOSE',
                    'percentage': 50,
                    'reason': 'TP1 reached',
                    'move_sl_to': position['entry_price'],  # Breakeven
                })
            elif position['direction'] == 'SHORT' and candle['low'] <= position['take_profit_1']:
                actions.append({
                    'action': 'PARTIAL_CLOSE',
                    'percentage': 50,
                    'reason': 'TP1 reached',
                    'move_sl_to': position['entry_price'],
                })
        
        # Trailing stop after TP1
        if position.get('tp1_hit'):
            new_sl = self._calculate_trailing_stop(position, candle, atr)
            if new_sl and self._is_better_stop(position, new_sl):
                actions.append({
                    'action': 'MODIFY_SL',
                    'new_stop_loss': new_sl,
                    'reason': 'Trailing stop update',
                })
        
        # Phase change exit
        if self._phase_contradicts_position(position, state):
            actions.append({
                'action': 'CLOSE_ALL',
                'reason': f'Phase changed to {state.market_phase.name} — contradicts position',
            })
        
        # Time-based management
        bars_open = candle.get('index', 0) - position.get('entry_bar', 0)
        if bars_open > self.config.get('max_bars_open', 100):
            if position.get('unrealized_pnl', 0) < 0:
                actions.append({
                    'action': 'CLOSE_ALL',
                    'reason': 'Time stop — position open too long without profit',
                })
        
        return actions
    
    def _calculate_trailing_stop(self, position, candle, atr):
        """Calculate new trailing stop level."""
        trail_distance = atr * self.config.get('trail_atr_multiplier', 2.0)
        
        if position['direction'] == 'LONG':
            new_sl = candle['high'] - trail_distance
            return new_sl if new_sl > position['stop_loss'] else None
        else:
            new_sl = candle['low'] + trail_distance
            return new_sl if new_sl < position['stop_loss'] else None
    
    def _is_better_stop(self, position, new_sl):
        """Check if new stop is better (tighter in profit direction)."""
        if position['direction'] == 'LONG':
            return new_sl > position['stop_loss']
        else:
            return new_sl < position['stop_loss']
    
    def _determine_order_type(self, signal):
        """Determine whether to use market, limit, or stop order."""
        signal_type = signal.get('signal_type', '')
        
        # Market orders for immediate-action signals
        if signal_type in ['SPRING_ENTRY', 'UTAD_ENTRY', 'CLIMAX_REVERSAL']:
            return 'MARKET'
        
        # Limit orders for pullback entries
        if 'PULLBACK' in signal_type or 'LPS' in signal_type or 'LPSY' in signal_type:
            return 'LIMIT'
        
        # Stop orders for breakout entries
        if 'SOS' in signal_type or 'SOW' in signal_type or 'BOS' in signal_type:
            return 'STOP'
        
        return 'MARKET'  # Default
```

---

## 7. การดำเนินการหลายกรอบเวลา (Multi-Timeframe Execution)

### 7.1 กรอบการดำเนินการ MTF

```python
class MultiTimeframeExecutor:
    """
    Coordinates analysis across multiple timeframes for optimal execution.
    
    Strategy:
    - HTF (Daily/4H): Determines DIRECTION (which phase, which bias)
    - MTF (1H): Determines AREA (where to look for entries)
    - LTF (15M/5M): Determines TIMING (when exactly to enter)
    """
    
    def __init__(self, config):
        self.config = config
        self.htf_state = SystemState()
        self.mtf_state = SystemState()
        self.ltf_state = SystemState()
        
        # Analysis engines per timeframe
        self.htf_analyzer = WyckoffAnalyzer(config, timeframe='H4')
        self.mtf_analyzer = WyckoffAnalyzer(config, timeframe='H1')
        self.ltf_analyzer = WyckoffAnalyzer(config, timeframe='M15')
    
    def on_htf_bar(self, candle, candles):
        """Process Higher Timeframe bar — direction bias."""
        result = self.htf_analyzer.process(candle, candles)
        self.htf_state = result['state']
        
        return {
            'bias': self._get_htf_bias(),
            'phase': self.htf_state.market_phase,
            'key_levels': result.get('key_levels', {}),
        }
    
    def on_mtf_bar(self, candle, candles):
        """Process Middle Timeframe bar — entry area identification."""
        result = self.mtf_analyzer.process(candle, candles)
        self.mtf_state = result['state']
        
        # Only generate signals if aligned with HTF
        htf_bias = self._get_htf_bias()
        
        if self._mtf_aligned_with_htf(htf_bias):
            return {
                'entry_zone': self._identify_entry_zone(),
                'awaiting_ltf_trigger': True,
            }
        
        return {'awaiting_ltf_trigger': False}
    
    def on_ltf_bar(self, candle, candles, mtf_context):
        """Process Lower Timeframe bar — precise entry timing."""
        if not mtf_context.get('awaiting_ltf_trigger'):
            return {'signals': []}
        
        result = self.ltf_analyzer.process(candle, candles)
        self.ltf_state = result['state']
        
        # Look for LTF trigger within MTF entry zone
        signals = []
        
        for event in result.get('events', []):
            if self._is_valid_ltf_trigger(event, mtf_context):
                signal = self._create_mtf_signal(event, candle)
                signals.append(signal)
        
        return {'signals': signals}
    
    def _get_htf_bias(self):
        """Get directional bias from HTF state."""
        phase = self.htf_state.market_phase
        
        if phase in [MarketPhase.ACCUMULATION_C, MarketPhase.ACCUMULATION_D,
                     MarketPhase.ACCUMULATION_E, MarketPhase.MARKUP]:
            return 'BULLISH'
        elif phase in [MarketPhase.DISTRIBUTION_C, MarketPhase.DISTRIBUTION_D,
                       MarketPhase.DISTRIBUTION_E, MarketPhase.MARKDOWN]:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _mtf_aligned_with_htf(self, htf_bias):
        """Check if MTF is aligned with HTF for entry."""
        mtf_phase = self.mtf_state.market_phase
        
        if htf_bias == 'BULLISH':
            return mtf_phase in [MarketPhase.ACCUMULATION_C, MarketPhase.ACCUMULATION_D,
                                MarketPhase.MARKUP]
        elif htf_bias == 'BEARISH':
            return mtf_phase in [MarketPhase.DISTRIBUTION_C, MarketPhase.DISTRIBUTION_D,
                                MarketPhase.MARKDOWN]
        return False
    
    def _is_valid_ltf_trigger(self, event, mtf_context):
        """Check if LTF event is a valid entry trigger."""
        htf_bias = self._get_htf_bias()
        
        if htf_bias == 'BULLISH':
            return event.get('event') in ['SPRING', 'TEST_OF_SPRING', 'SOS', 'CHOCH'] \
                   and event.get('direction', event.get('bias', '')) == 'BULLISH'
        elif htf_bias == 'BEARISH':
            return event.get('event') in ['UTAD', 'TEST_OF_UTAD', 'SOW', 'CHOCH'] \
                   and event.get('direction', event.get('bias', '')) == 'BEARISH'
        return False
```

### 7.2 เมทริกซ์การตัดสินใจ MTF

```
Multi-Timeframe Decision Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HTF (4H/Daily)          MTF (1H)              LTF (15M/5M)
──────────────          ─────────             ──────────────

Accumulation D    →     Markup pullback  →    Bullish ChoCh     = STRONG BUY
(SOS confirmed)         (HL forming)          (entry trigger)

Markup            →     Re-accumulation →     Spring/Test       = BUY
(HH+HL intact)         (range at HL)         (entry trigger)

Distribution D    →     Markdown rally   →    Bearish ChoCh     = STRONG SELL
(SOW confirmed)         (LH forming)          (entry trigger)

Markdown          →     Re-distribution  →    UTAD/Test         = SELL
(LH+LL intact)         (range at LH)         (entry trigger)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 8. Pseudocode การนำไปใช้แบบสมบูรณ์

### 8.1 ลูปหลักการเทรด (Main Trading Loop)

```python
class WyckoffTradingBot:
    """
    Complete Wyckoff trading system — main orchestration class.
    """
    
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        
        # Core components
        self.data_feed = DataFeedManager(self.config['data'])
        self.indicator_engine = IndicatorEngine(self.config['indicators'])
        self.swing_detector = SwingDetector(**self.config['swing_detection'])
        self.volume_analyzer = VSAScanner(self.config['vsa'])
        
        # Phase detection
        self.accumulation_detector = AccumulationDetector(self.config)
        self.distribution_detector = DistributionDetector(self.config)
        self.structure_engine = MarketStructureEngine(self.config)
        
        # MTF
        self.mtf_executor = MultiTimeframeExecutor(self.config)
        
        # Execution
        self.signal_generator = SignalGenerator(self.config)
        self.signal_validator = SignalValidator(self.config)
        self.position_sizer = PositionSizer()
        self.order_manager = OrderManager(self.config['broker_api'], self.config)
        
        # State
        self.state = SystemState()
        self.account = self._get_account_state()
        
    def run(self):
        """Main event loop."""
        while self.data_feed.is_active():
            # Get next bar
            bar_event = self.data_feed.get_next_bar()
            
            if bar_event is None:
                continue
            
            timeframe = bar_event['timeframe']
            candle = bar_event['candle']
            candles = bar_event['history']
            
            # Process based on timeframe
            if timeframe == self.config['htf']:
                self._process_htf(candle, candles)
            elif timeframe == self.config['mtf']:
                self._process_mtf(candle, candles)
            elif timeframe == self.config['ltf']:
                self._process_ltf(candle, candles)
            
            # Manage existing positions on every bar
            self._manage_positions(candle, timeframe)
    
    def _process_htf(self, candle, candles):
        """Process Higher Timeframe bar."""
        # Update indicators
        indicators = self.indicator_engine.update(candles)
        atr = indicators['atr']
        avg_volume = indicators['avg_volume']
        
        # Update structure
        structure_result = self.structure_engine.process_bar(
            candle, len(candles)-1, candles, atr, avg_volume
        )
        
        # Update Wyckoff phase
        accum_result = self.accumulation_detector.update(
            candle, len(candles)-1, avg_volume, atr, 
            structure_result['trend']
        )
        dist_result = self.distribution_detector.update(
            candle, len(candles)-1, avg_volume, atr,
            structure_result['trend']
        )
        
        # Determine primary phase
        if accum_result['confidence'] > dist_result['confidence']:
            self.state.market_phase = self._map_accum_state(accum_result['state'])
            self.state.phase_confidence = accum_result['confidence']
        else:
            self.state.market_phase = self._map_dist_state(dist_result['state'])
            self.state.phase_confidence = dist_result['confidence']
        
        # Update MTF executor
        self.mtf_executor.on_htf_bar(candle, candles)
        
        # Log HTF state
        self._log_state('HTF', candle)
    
    def _process_mtf(self, candle, candles):
        """Process Middle Timeframe bar."""
        indicators = self.indicator_engine.update(candles)
        atr = indicators['atr']
        avg_volume = indicators['avg_volume']
        
        # VSA analysis
        context = self._build_vsa_context(candle, candles, indicators)
        vsa_signals = self.volume_analyzer.scan(candle, candles, context)
        
        if vsa_signals:
            self.state.last_vsa_signal = vsa_signals[0]
        
        # MTF structure
        structure = self.structure_engine.process_bar(
            candle, len(candles)-1, candles, atr, avg_volume
        )
        
        # Update state
        self.state.structure_state = StructureState[structure['trend']] \
            if structure['trend'] in StructureState.__members__ else StructureState.UNKNOWN
        
        # MTF executor update
        mtf_result = self.mtf_executor.on_mtf_bar(candle, candles)
        
        # If MTF aligned, prepare for LTF triggers
        self.state._mtf_ready = mtf_result.get('awaiting_ltf_trigger', False)
    
    def _process_ltf(self, candle, candles):
        """Process Lower Timeframe bar — entry timing."""
        if not getattr(self.state, '_mtf_ready', False):
            return
        
        indicators = self.indicator_engine.update(candles)
        atr = indicators['atr']
        avg_volume = indicators['avg_volume']
        
        # Generate signals
        signals = self.signal_generator.generate_signals(self.state, candle, atr)
        
        for signal in signals:
            # Validate
            is_valid, reason = self.signal_validator.validate(
                signal, self.state, self.account
            )
            
            if not is_valid:
                self._log(f"Signal rejected: {reason}")
                continue
            
            # Size position
            market_info = self.data_feed.get_market_info(signal.get('symbol'))
            position_size = self.position_sizer.calculate_size(
                signal, self.account, market_info
            )
            
            if position_size['lot_size'] <= 0:
                continue
            
            # Execute
            result = self.order_manager.place_entry_order(signal, position_size)
            
            if result['status'] in ['FILLED', 'PENDING']:
                self._log(f"Order placed: {signal['signal_type']} "
                         f"{signal['direction']} {position_size['lot_size']} lots "
                         f"@ {signal['entry_price']:.5f}")
                
                # Update state
                self.state.active_positions.append({
                    'signal': signal,
                    'size': position_size,
                    'order': result,
                    'entry_bar': len(candles) - 1,
                })
    
    def _manage_positions(self, candle, timeframe):
        """Manage all open positions."""
        if timeframe != self.config['ltf']:
            return  # Only manage on LTF bars
        
        indicators = self.indicator_engine.get_current()
        atr = indicators.get('atr', 0.001)
        
        for position in self.state.active_positions[:]:
            actions = self.order_manager.manage_position(
                position, candle, self.state, atr
            )
            
            for action in actions:
                self._execute_management_action(position, action)
    
    def _execute_management_action(self, position, action):
        """Execute a position management action."""
        if action['action'] == 'PARTIAL_CLOSE':
            self.order_manager.partial_close(
                position, action['percentage']
            )
            position['tp1_hit'] = True
            if 'move_sl_to' in action:
                position['stop_loss'] = action['move_sl_to']
        
        elif action['action'] == 'CLOSE_ALL':
            self.order_manager.close_position(position)
            self.state.active_positions.remove(position)
        
        elif action['action'] == 'MODIFY_SL':
            position['stop_loss'] = action['new_stop_loss']
            self.order_manager.modify_stop(position, action['new_stop_loss'])
```

---

## 9. เมตริกประสิทธิภาพ (Performance Metrics)

### 9.1 ตัวชี้วัดประสิทธิภาพหลัก (KPI)

```python
class PerformanceTracker:
    """Track and calculate trading performance metrics."""
    
    def calculate_metrics(self, trades):
        """
        Calculate comprehensive performance metrics.
        """
        if not trades:
            return {}
        
        # Basic metrics
        total_trades = len(trades)
        winners = [t for t in trades if t['pnl'] > 0]
        losers = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = len(winners) / total_trades if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in winners]) if winners else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losers])) if losers else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winners)
        gross_loss = abs(sum(t['pnl'] for t in losers))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Risk-adjusted metrics
        returns = [t['pnl_pct'] for t in trades]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Drawdown
        equity_curve = np.cumsum([t['pnl'] for t in trades])
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Per-phase metrics
        phase_metrics = {}
        for phase in set(t.get('phase', 'UNKNOWN') for t in trades):
            phase_trades = [t for t in trades if t.get('phase') == phase]
            phase_winners = [t for t in phase_trades if t['pnl'] > 0]
            phase_metrics[phase] = {
                'trades': len(phase_trades),
                'win_rate': len(phase_winners) / len(phase_trades) if phase_trades else 0,
                'avg_rr': np.mean([t.get('actual_rr', 0) for t in phase_trades]),
            }
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'expectancy': expectancy,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_rr': avg_win / avg_loss if avg_loss > 0 else 0,
            'best_trade': max(t['pnl'] for t in trades),
            'worst_trade': min(t['pnl'] for t in trades),
            'phase_metrics': phase_metrics,
            'consecutive_losses_max': self._max_consecutive(trades, 'loss'),
            'consecutive_wins_max': self._max_consecutive(trades, 'win'),
        }
    
    def _max_consecutive(self, trades, type_):
        """Calculate max consecutive wins or losses."""
        max_consec = 0
        current = 0
        for t in trades:
            if (type_ == 'win' and t['pnl'] > 0) or (type_ == 'loss' and t['pnl'] <= 0):
                current += 1
                max_consec = max(max_consec, current)
            else:
                current = 0
        return max_consec
```

### 9.2 มาตรฐานประสิทธิภาพที่คาดหวัง

| Metric | Target (Forex) | Target (Crypto) | Notes |
|---|---|---|---|
| Win Rate | 45–55% | 40–50% | Lower in crypto due to volatility |
| Profit Factor | > 1.5 | > 1.8 | Higher target in crypto (larger wins) |
| Average R:R | > 2.0 | > 2.5 | |
| Max Drawdown | < 15% | < 20% | Crypto allows slightly more |
| Sharpe Ratio | > 1.5 | > 1.0 | Crypto more volatile |
| Monthly Return | 3–8% | 5–15% | Risk-adjusted |
| Trades per Month | 15–30 | 20–40 | |

---

## 10. การจัดการข้อผิดพลาดและกรณีพิเศษ

### 10.1 ประเภทข้อผิดพลาดและการจัดการ

```python
class ErrorHandler:
    """
    Handle system errors gracefully.
    """
    
    def handle_error(self, error_type, context, error):
        """
        Centralized error handling.
        """
        handlers = {
            'DATA_FEED_ERROR': self._handle_data_error,
            'BROKER_CONNECTION_ERROR': self._handle_broker_error,
            'ORDER_REJECTION': self._handle_order_rejection,
            'INSUFFICIENT_MARGIN': self._handle_margin_error,
            'PHASE_DETECTION_ERROR': self._handle_analysis_error,
            'POSITION_MISMATCH': self._handle_position_mismatch,
        }
        
        handler = handlers.get(error_type, self._handle_unknown_error)
        return handler(context, error)
    
    def _handle_data_error(self, context, error):
        """Handle missing or corrupted data."""
        return {
            'action': 'SKIP_BAR',
            'close_positions': False,
            'alert': 'WARNING',
            'message': f'Data error: {error}. Skipping bar.',
            'retry_after': 5  # seconds
        }
    
    def _handle_broker_error(self, context, error):
        """Handle broker disconnection."""
        return {
            'action': 'HALT_NEW_ORDERS',
            'close_positions': False,  # Don't close — positions have SL set
            'alert': 'CRITICAL',
            'message': f'Broker disconnected: {error}. Halting new orders.',
            'retry_after': 10
        }
    
    def _handle_order_rejection(self, context, error):
        """Handle order rejection."""
        return {
            'action': 'LOG_AND_CONTINUE',
            'close_positions': False,
            'alert': 'WARNING',
            'message': f'Order rejected: {error}. Will retry on next signal.',
            'retry_after': 0
        }
```

### 10.2 กรณีพิเศษ (Edge Cases)

| Edge Case | Handling | Notes |
|---|---|---|
| Gap opens beyond SL | Accept slippage, record actual loss | Calculate worst-case in position sizing |
| Multiple signals same bar | Take highest confidence only | Avoid over-trading |
| Phase change while in position | Evaluate: close if conflicting | Don't panic-close profitable positions |
| Volume data missing | Fall back to spread-only analysis | Reduce confidence by 30% |
| Whipsaw (rapid ChoCh) | Require confirmation period | Min 3 bars between ChoCh trades |
| Flash crash / spike | Widen stop tolerance during events | Use guaranteed stops if available |
| Low liquidity period | Reduce position sizes | Asian session for Forex |
| News event gap | No new entries 30min before/after | Close or tighten existing |

---

## 11. กรอบการทดสอบย้อนหลัง (Backtesting Framework)

### 11.1 สถาปัตยกรรมการทดสอบย้อนหลัง

```python
class WyckoffBacktester:
    """
    Backtesting framework for the Wyckoff trading system.
    """
    
    def __init__(self, config, data_provider):
        self.config = config
        self.data = data_provider
        self.trading_system = WyckoffTradingBot(config)
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, symbol, start_date, end_date, initial_balance=10000):
        """
        Run full backtest over historical data.
        """
        # Load data for all timeframes
        data = self.data.load(symbol, start_date, end_date, 
                            timeframes=self.config['timeframes'])
        
        account = {
            'balance': initial_balance,
            'equity': initial_balance,
            'peak_equity': initial_balance,
            'margin_used': 0,
            'daily_loss': 0,
        }
        
        # Simulate bar-by-bar
        for bar_event in self._generate_bar_events(data):
            # Process through trading system
            result = self.trading_system.process_bar_backtest(
                bar_event, account
            )
            
            # Record results
            if result.get('trade_closed'):
                self.trades.append(result['trade_closed'])
                account['balance'] += result['trade_closed']['pnl']
                account['equity'] = account['balance']
                account['peak_equity'] = max(account['peak_equity'], account['equity'])
            
            self.equity_curve.append(account['equity'])
        
        # Calculate final metrics
        metrics = PerformanceTracker().calculate_metrics(self.trades)
        
        return {
            'metrics': metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'final_balance': account['balance'],
            'total_return_pct': (account['balance'] - initial_balance) / initial_balance * 100,
        }
    
    def walk_forward_optimization(self, symbol, full_period, 
                                   train_pct=0.7, n_folds=5):
        """
        Walk-forward analysis to avoid overfitting.
        """
        results = []
        fold_size = len(full_period) // n_folds
        
        for fold in range(n_folds):
            # Split into train and test
            train_end = int(fold_size * (fold + train_pct))
            test_start = train_end
            test_end = fold_size * (fold + 1)
            
            # Optimize on training set
            best_params = self._optimize_parameters(
                symbol, full_period[:train_end]
            )
            
            # Test on out-of-sample
            test_result = self.run_backtest(
                symbol, 
                full_period[test_start], 
                full_period[test_end],
                config_override=best_params
            )
            
            results.append({
                'fold': fold,
                'train_period': f"{full_period[0]} to {full_period[train_end]}",
                'test_period': f"{full_period[test_start]} to {full_period[test_end]}",
                'params': best_params,
                'metrics': test_result['metrics'],
            })
        
        return results
```

---

## 12. การนำไปใช้งานจริง (Production Deployment)

### 12.1 รายการตรวจสอบการนำไปใช้งาน

```
Production Deployment Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Backtesting completed with positive results (> 1000 trades)
[ ] Walk-forward analysis shows consistent performance
[ ] Paper trading for minimum 30 days with live data
[ ] Risk parameters validated against worst-case scenarios
[ ] Broker API connection tested (order placement, modification, closing)
[ ] Error handling tested (disconnection, rejection, timeout)
[ ] Monitoring and alerting system active
[ ] Kill switch functional (emergency shutdown)
[ ] Database for trade logging and state persistence
[ ] Multi-timeframe data feeds validated (no gaps, correct timestamps)
[ ] Position reconciliation with broker (periodic checks)
[ ] Disaster recovery plan documented
[ ] Maximum drawdown trigger tested
[ ] News calendar integration (high-impact event avoidance)
[ ] Latency monitoring (order execution speed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 12.2 เมตริกแดชบอร์ดการตรวจสอบ

| Category | Metric | Alert Threshold |
|---|---|---|
| **System Health** | Data feed latency | > 5 seconds |
| **System Health** | Broker connection status | Disconnected > 30s |
| **System Health** | CPU/Memory usage | > 80% |
| **Trading** | Open positions count | > max_positions |
| **Trading** | Daily P&L | Loss > 3% |
| **Trading** | Win rate (rolling 20) | < 30% |
| **Trading** | Consecutive losses | > 5 |
| **Risk** | Current drawdown | > 10% |
| **Risk** | Margin utilization | > 50% |
| **Risk** | Position correlation | > 3 same direction |
| **Analysis** | Phase confidence | < 0.50 for > 2 hours |
| **Analysis** | MTF disagreement | All TFs conflicting |

### 12.3 โครงสร้างไฟล์กำหนดค่า

```python
PRODUCTION_CONFIG = {
    # Timeframes
    'htf': 'H4',
    'mtf': 'H1', 
    'ltf': 'M15',
    'timeframes': ['H4', 'H1', 'M15'],
    
    # Symbols
    'symbols': ['EURUSD', 'GBPUSD', 'BTCUSD', 'ETHUSD'],
    
    # Analysis parameters
    'swing_detection': {
        'lookback': 3,
        'min_swing_atr': 0.5,
        'min_bars_between': 3,
    },
    'indicators': {
        'atr_period': 14,
        'volume_avg_period': 20,
        'ema_fast': 20,
        'ema_slow': 50,
    },
    'vsa': {
        'volume_avg_period': 20,
        'spread_avg_period': 20,
    },
    
    # Signal generation
    'min_confidence': 0.65,
    'min_risk_reward': 2.0,
    'max_signals_per_bar': 2,
    
    # Risk management
    'risk': {
        'max_risk_per_trade': 2.0,       # percent
        'max_daily_loss': 4.0,           # percent
        'max_weekly_loss': 6.0,          # percent
        'max_drawdown': 15.0,            # percent
        'max_positions': 5,
        'max_correlated': 3,
        'trail_atr_multiplier': 2.0,
        'max_bars_open': 100,
    },
    
    # Execution
    'execution': {
        'slippage_estimate': 0.5,        # pips
        'max_spread_ratio': 0.1,         # max spread as ratio of stop
        'news_blackout_minutes': 30,
    },
    
    # Broker
    'broker_api': {
        'type': 'MT5',                   # or 'CCXT' for crypto
        'server': 'live',
        'account_id': 'XXXXX',
    },
}
```

---

## 13. เอกสารอ้างอิง

### 13.1 เอกสารอ้างอิงการออกแบบระบบ

1. Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies*. Wiley.
2. Chan, E.P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
3. Narang, R.K. (2013). *Inside the Black Box: A Simple Guide to Quantitative and High Frequency Trading*. Wiley.

### 13.2 เอกสารอ้างอิงวิธี Wyckoff

4. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. Wyckoff Associates.
5. Pruden, H.O. (2007). *The Three Skills of Top Trading*. Wiley.
6. Weis, D.H. (2013). *Trades About to Happen*. Wiley.

### 13.3 เอกสารอ้างอิงการจัดการความเสี่ยง

7. Vince, R. (1992). *The Mathematics of Money Management*. Wiley.
8. Van Tharp, K. (2006). *Trade Your Way to Financial Freedom*. McGraw-Hill.

### 13.4 เอกสารอ้างอิงวิศวกรรมซอฟต์แวร์

9. Gamma, E. et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. — State Machine pattern.
10. Martin, R.C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.

---

## สรุป

เอกสารนี้ให้ขั้นตอนการดำเนินการแบบสมบูรณ์สำหรับระบบเทรดเชิงอัลกอริทึมที่ใช้ Wyckoff เป็นพื้นฐาน ประกอบด้วย:

1. **State Machine** — Tracks all Wyckoff phases and transitions with formal rules
2. **Signal Generation** — 12+ entry signal types with precise conditions
3. **Risk Management** — Complete risk parameter tables with dynamic adjustment
4. **Position Sizing** — Kelly-criterion-adapted sizing with drawdown scaling
5. **Order Management** — Full lifecycle management (entry, trail, partial, exit)
6. **Multi-Timeframe** — HTF direction → MTF area → LTF timing framework
7. **Full Implementation** — Production-ready pseudocode with all components
8. **Performance Tracking** — Comprehensive metrics and benchmarks
9. **Error Handling** — Graceful degradation for all failure modes
10. **Deployment** — Checklist and monitoring for live trading

ระบบนี้ออกแบบมาสำหรับทั้งตลาด Forex และคริปโต พร้อมการปรับใช้เฉพาะสินทรัพย์ที่บันทึกไว้ในไฟล์ก่อนหน้าของโมดูลนี้

---

> **จบโมดูล 02 — วิธี Wyckoff และโครงสร้างตลาด**
> 
> กลับไปที่: `00_overview.md` สำหรับการนำทางโมดูล
