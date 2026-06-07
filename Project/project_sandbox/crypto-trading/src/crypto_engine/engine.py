"""Engine — deterministic Step 1 `analyze`.

Reads stored candles -> computes features per TF -> signals -> confluence -> bias
-> assembles the §6 contract JSON (elliott/summaries/plan = null in v1).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pandas as pd

from .config import EngineConfig, load_config
from .contract import DataWindow, Levels, Meta, Regime, Step1Output
from .data import backfill as B
from .data import store as S
from .features import indicators as I
from .features import patterns as P
from .features import structure as ST
from .signals import confluence as C
from .signals import decision as D
from .signals.registry import CandleReading, SignalInputs, build_signals


def _ms_to_date(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def analyze(
    cfg: EngineConfig, symbol: str, refresh: bool = False, root: str = S.DEFAULT_ROOT
) -> Step1Output:
    if refresh:
        B.backfill_symbol(cfg, symbol, root=root)

    tfs = cfg.universe.timeframes
    anchor_tf = cfg.features.ma.anchor_tf
    fcfg = cfg.features

    # ---- per-TF features ----
    candles: dict[str, pd.DataFrame] = {}
    rsi_by_tf: dict[str, float] = {}
    structure_by_tf: dict[str, str] = {}
    pivots_by_tf: dict[str, list] = {}
    for tf in tfs:
        df = S.read_candles(symbol, tf, root)
        if df.empty:
            raise RuntimeError(f"no stored candles for {symbol} {tf} — run a backfill first")
        candles[tf] = df
        rsi_by_tf[tf] = float(I.rsi(df["close"], fcfg.rsi.period).iloc[-1])
        piv = ST.find_pivots(df, fcfg.structure.pivot_lookback)
        pivots_by_tf[tf] = piv
        structure_by_tf[tf] = ST.classify_structure(piv, fcfg.structure.swing_count)

    # ---- anchor-TF features (1d) ----
    adf = candles[anchor_tf]
    close = adf["close"]
    close_last = float(close.iloc[-1])
    atr_series = I.atr(adf["high"], adf["low"], close, fcfg.atr.period)
    atr_last = float(atr_series.iloc[-1])

    ma_label, ma_vals = I.ma_stack(close, fcfg.ma.periods, fcfg.ma.type)
    ma_level_values = [v for v in ma_vals.values() if not math.isnan(v)]

    vol_label = ST.vol_regime(
        atr_series, fcfg.vol_regime.lookback, fcfg.vol_regime.expansion_mult, fcfg.vol_regime.contraction_mult
    )
    ma20 = ma_vals.get("ma20", float("nan"))
    price_dist = ST.price_vs_ma_dist(close_last, ma20, atr_last)

    anchor_pivots = pivots_by_tf[anchor_tf]
    support, resistance = ST.support_resistance(
        adf, anchor_pivots, atr_last, ma_levels=ma_level_values,
        cluster_atr_mult=fcfg.levels.cluster_atr_mult,
        max_support=fcfg.levels.max_support, max_resistance=fcfg.levels.max_resistance,
    )

    # ---- candle pattern (context-filtered) on candle TF ----
    ctf = fcfg.candle.tf
    cdf = candles.get(ctf, adf)
    hit = P.detect_last(cdf, fcfg.candle.enabled)
    ctx = atr_last * fcfg.candle.context_atr if atr_last > 0 else 0.0
    near_sup = any(abs(close_last - s) <= ctx for s in support)
    near_res = any(abs(close_last - r) <= ctx for r in resistance)
    candle = CandleReading(hit.direction, hit.name, near_sup, near_res)

    # ---- signals -> confluence -> bias ----
    inp = SignalInputs(
        rsi_by_tf=rsi_by_tf, structure_by_tf=structure_by_tf, ma_stack_label=ma_label,
        vol_regime_label=vol_label, price_dist=price_dist, candle=candle, candle_tf=ctf,
    )
    signals = build_signals(inp, cfg)
    conf = C.derive(signals, structure_by_tf, tfs, cfg)

    # ---- deterministic regime + invalidation ----
    structure_1d = structure_by_tf.get(anchor_tf, "mixed")
    trend = D.derive_trend(ma_label, structure_1d)
    invalidation = D.compute_invalidation(
        conf.bias.direction, anchor_pivots, atr_last, close_last, vol_label, cfg
    )

    # ---- assemble §6 ----
    return Step1Output(
        meta=Meta(
            symbol=symbol,
            asset_class=cfg.universe.asset_class,
            timeframes=tfs,
            generated_at=_now_iso(),
            data_window=DataWindow(**{"from": cfg.data.history_start, "to": _ms_to_date(int(adf["timestamp"].iloc[-1]))}),
            engine_version=cfg.engine_version,
        ),
        regime=Regime(
            trend=trend,
            structure=D.structure_text(structure_1d),
            note=D.regime_note(ma_label, ma_vals, rsi_by_tf.get(anchor_tf), fcfg.rsi.oversold, fcfg.rsi.overbought),
        ),
        bias=conf.bias,
        levels=Levels(support=support, resistance=resistance, invalidation=invalidation),
        signals=signals,
        confluence_score=conf.score,
        confidence=conf.confidence,
        caveats=conf.caveats,
        elliott=None, summaries=None, plan=None,  # interpretive (LLM) — null in v1
    )


def analyze_default(symbol: str = "BTCUSDT", config_path: str = "config/engine.yaml", refresh: bool = False) -> Step1Output:
    return analyze(load_config(config_path), symbol, refresh=refresh)
