"""Load + validate config/engine.yaml into typed models.

All tuning params (weights, periods, thresholds) live in YAML so deterministic
output stays reproducible and diffable. Nothing here is hardcoded in logic.
Mirrors doc/03-signal-logic-spec.md §7.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class Universe(BaseModel):
    symbols: list[str]
    timeframes: list[str]
    extra_fetch_timeframes: list[str] = ["1w"]
    asset_class: str


class DataCfg(BaseModel):
    exchange: str = "binance"
    history_start: str = "2024-01-01"
    drop_unclosed_candle: bool = True
    fetch_limit: int = 1000


class MACfg(BaseModel):
    periods: list[int] = [20, 50, 100]
    type: Literal["sma", "ema"] = "ema"
    anchor_tf: str = "1d"


class RSICfg(BaseModel):
    period: int = 14
    oversold: float = 30
    overbought: float = 70


class ATRCfg(BaseModel):
    period: int = 14


class StructureCfg(BaseModel):
    pivot_lookback: int = 3
    swing_count: int = 4
    swing_atr_mult: float = 0.5


class CandleCfg(BaseModel):
    tf: str = "1d"
    context_atr: float = 0.5
    enabled: list[str] = ["engulfing", "hammer", "shooting_star", "doji"]


class VolRegimeCfg(BaseModel):
    lookback: int = 100
    expansion_mult: float = 1.5
    contraction_mult: float = 0.7


class PriceDistCfg(BaseModel):
    stretch: float = 2.5


class LevelsCfg(BaseModel):
    max_support: int = 3
    max_resistance: int = 3
    cluster_atr_mult: float = 0.5


class FeaturesCfg(BaseModel):
    ma: MACfg = Field(default_factory=MACfg)
    rsi: RSICfg = Field(default_factory=RSICfg)
    atr: ATRCfg = Field(default_factory=ATRCfg)
    structure: StructureCfg = Field(default_factory=StructureCfg)
    candle: CandleCfg = Field(default_factory=CandleCfg)
    vol_regime: VolRegimeCfg = Field(default_factory=VolRegimeCfg)
    price_dist: PriceDistCfg = Field(default_factory=PriceDistCfg)
    levels: LevelsCfg = Field(default_factory=LevelsCfg)


class ConvictionCfg(BaseModel):
    medium_margin: float = 0.15
    high_margin: float = 0.35


class SignalsCfg(BaseModel):
    weights: dict[str, float]
    conviction: ConvictionCfg = Field(default_factory=ConvictionCfg)


class ConfidenceCfg(BaseModel):
    floor: float = 0.45


class MacroRegimeCfg(BaseModel):
    active: Literal["aligned", "neutral", "conflicting"] = "neutral"
    aligned: float = 1.0
    neutral: float = 0.85
    conflicting: float = 0.65

    @property
    def factor(self) -> float:
        return getattr(self, self.active)


class InvalidationCfg(BaseModel):
    atr_mult: float = 0.5
    confirm: str = "weekly_close"
    min_atr_dist: float = 1.0
    expansion_widen: float = 1.3


class ElliottCfg(BaseModel):
    enabled: bool = False
    weight: float = 0.05


class OutputCfg(BaseModel):
    dir: str = "output"
    write_markdown: bool = True


class EngineConfig(BaseModel):
    engine_version: str = "0.1.0"
    universe: Universe
    data: DataCfg = Field(default_factory=DataCfg)
    features: FeaturesCfg = Field(default_factory=FeaturesCfg)
    signals: SignalsCfg
    confidence: ConfidenceCfg = Field(default_factory=ConfidenceCfg)
    macro_regime: MacroRegimeCfg = Field(default_factory=MacroRegimeCfg)
    invalidation: InvalidationCfg = Field(default_factory=InvalidationCfg)
    elliott: ElliottCfg = Field(default_factory=ElliottCfg)
    output: OutputCfg = Field(default_factory=OutputCfg)


def load_config(path: str | Path = "config/engine.yaml") -> EngineConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return EngineConfig.model_validate(raw)
