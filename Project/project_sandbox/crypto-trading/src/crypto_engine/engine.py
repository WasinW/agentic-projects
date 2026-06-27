"""Engine — deterministic Step 1 `analyze`.

Reads stored candles -> computes features per TF -> signals -> confluence -> bias
-> assembles the §6 contract JSON (elliott/summaries/plan = null in v1).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pandas as pd

from .config import EngineConfig, load_config
from .contract import DataWindow, Levels, Meta, Regime, Signal, Step1Output
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
    cfg: EngineConfig,
    symbol: str,
    refresh: bool = False,
    root: str = S.DEFAULT_ROOT,
    interpret: bool = False,
    llm_client=None,
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
    structure_1d = structure_by_tf.get(anchor_tf, "mixed")

    def _invalidation(direction: str):
        return D.compute_invalidation(direction, anchor_pivots, atr_last, close_last, vol_label, cfg)

    def _assemble(conf_, signals_, elliott=None, summaries=None, plan=None) -> Step1Output:
        return Step1Output(
            meta=Meta(
                symbol=symbol, asset_class=cfg.universe.asset_class, timeframes=tfs,
                generated_at=_now_iso(),
                data_window=DataWindow(**{"from": cfg.data.history_start, "to": _ms_to_date(int(adf["timestamp"].iloc[-1]))}),
                engine_version=cfg.engine_version,
            ),
            regime=Regime(
                trend=D.derive_trend(ma_label, structure_1d),
                structure=D.structure_text(structure_1d),
                note=D.regime_note(ma_label, ma_vals, rsi_by_tf.get(anchor_tf), fcfg.rsi.oversold, fcfg.rsi.overbought),
            ),
            bias=conf_.bias,
            levels=Levels(support=support, resistance=resistance, invalidation=_invalidation(conf_.bias.direction)),
            signals=signals_, confluence_score=conf_.score, confidence=conf_.confidence, caveats=conf_.caveats,
            elliott=elliott, summaries=summaries, plan=plan,
        )

    out = _assemble(conf, signals)  # deterministic (elliott/summaries/plan = null)
    if not interpret:
        return out

    # ---- interpretive LLM layer (Step 1.5) ----
    from . import interpret as I_

    def _recent(kind: str, n: int = 3) -> list[float]:
        return [round(p.price, 2) for p in anchor_pivots if p.kind == kind][-n:]

    digest = {
        "meta": out.meta.model_dump(by_alias=True),
        "regime": out.regime.model_dump(),
        "bias": out.bias.model_dump(),
        "confluence_score": out.confluence_score.model_dump(),
        "confidence": out.confidence,
        "levels": out.levels.model_dump(),
        "signals": [s.model_dump() for s in out.signals],
        "per_timeframe": {
            tf: {
                "rsi": round(rsi_by_tf[tf], 2),
                "structure": structure_by_tf[tf],
                "last_close": round(float(candles[tf]["close"].iloc[-1]), 2),
            }
            for tf in tfs
        },
        "anchor_tf": anchor_tf,
        "ma_values": {k: round(v, 2) for k, v in ma_vals.items() if v == v},
        "atr": round(atr_last, 2),
        "vol_regime": vol_label,
        "recent_swing_highs_1d": _recent("high"),
        "recent_swing_lows_1d": _recent("low"),
        "caveats": out.caveats,
    }

    res = I_.interpret(out, digest, cfg, client=llm_client)

    # fold the single Elliott signal into confluence (ADR 0007 — low weight, supporting view)
    if cfg.elliott.weight and "elliott_1d" not in {s.name for s in signals}:
        signals = [*signals, Signal(name="elliott_1d", value=res.elliott_value, vote=res.elliott_vote, weight=cfg.elliott.weight)]
        conf = C.derive(signals, structure_by_tf, tfs, cfg)

    return _assemble(conf, signals, elliott=res.elliott, summaries=res.summaries, plan=res.plan)


def analyze_default(symbol: str = "BTCUSDT", config_path: str = "config/engine.yaml", refresh: bool = False) -> Step1Output:
    return analyze(load_config(config_path), symbol, refresh=refresh)
