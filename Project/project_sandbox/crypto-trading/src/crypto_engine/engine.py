"""Engine — deterministic Step 1 `analyze`.

Reads stored candles -> computes features per TF -> signals -> confluence -> bias
-> assembles the §6 contract JSON (elliott/summaries/plan = null in v1).

The pure deterministic computation is factored into `deterministic(...)` so it can
run on any point-in-time candle slice — the backtest harness replays it over history
(imports the SAME pipeline; never re-implements signal logic).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd

from .config import EngineConfig, load_config
from .contract import DataWindow, Levels, Meta, Plan, Regime, Signal, Step1Output
from .data import backfill as B
from .data import store as S
from .features import indicators as I
from .features import patterns as P
from .features import structure as ST
from .signals import confluence as C
from .signals import decision as D
from .signals.confluence import ConfluenceResult
from .signals.registry import CandleReading, SignalInputs, build_signals


def _ms_to_date(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DetResult:
    """Everything the deterministic pass produced — reused by the interpret path
    (digest + elliott fold) and by the backtest (bias / confluence at a close)."""

    cfg: EngineConfig
    symbol: str
    tfs: list[str]
    anchor_tf: str
    candles: dict[str, pd.DataFrame]
    adf: pd.DataFrame
    close_last: float
    atr_last: float
    ma_label: str
    ma_vals: dict[str, float]
    vol_label: str
    price_dist: float
    support: list[float]
    resistance: list[float]
    anchor_pivots: list
    rsi_by_tf: dict[str, float]
    structure_by_tf: dict[str, str]
    structure_1d: str
    signals: list[Signal]
    conf: ConfluenceResult
    out: Step1Output = field(default=None)  # type: ignore[assignment]


def _deterministic_plan(det: DetResult, conf: ConfluenceResult, trend: str, inv) -> Plan:
    """Deterministic playbook + entry zone + stop + position sizing (doc/03 §4 + sizing).

    Code-owned per spec §6 ('deterministic seed of plan.playbook'); the LLM only enriches
    targets / r_r / prose later. targets + r_r stay None here (LLM-owned)."""
    cfg = det.cfg
    pb = D.select_playbook(trend, conf.bias.direction, conf.bias.conviction, det.vol_label, conf.confidence, cfg)
    entry_zone, entry_px = D.entry_from_source(pb.entry_source, det.support, det.resistance, det.close_last)
    if entry_zone is None:  # stand-aside family — no position
        return Plan(playbook=pb.playbook, note=pb.reason, sizing_note="stand-aside — no position")
    ps = D.position_size(entry_px, inv.price, cfg)
    return Plan(
        playbook=pb.playbook, entry_zone=entry_zone, stop=inv.price,
        sizing_note=ps.note if ps else "sizing disabled", note=pb.reason,
    )


def _build_output(
    det: DetResult,
    conf: ConfluenceResult,
    signals: list[Signal],
    elliott=None,
    summaries=None,
    llm_plan=None,
) -> Step1Output:
    """Assemble a §6 Step1Output from a DetResult + a (possibly re-derived) confluence."""
    cfg = det.cfg
    adf = det.adf
    fcfg = cfg.features
    inv = D.compute_invalidation(
        conf.bias.direction, det.anchor_pivots, det.atr_last, det.close_last, det.vol_label, cfg
    )
    trend = D.derive_trend(det.ma_label, det.structure_1d)

    plan = _deterministic_plan(det, conf, trend, inv)
    if llm_plan is not None:  # LLM enriches targets / r_r / prose; deterministic playbook wins
        plan.targets = llm_plan.targets
        plan.r_r = llm_plan.r_r
        if llm_plan.note:
            plan.note = f"{plan.note} · {llm_plan.note}"

    # caveat surface #3: sub-floor confidence forced stand-aside
    caveats = list(conf.caveats)
    if conf.confidence < cfg.confidence.floor:
        caveats.append(
            f"confidence {round(conf.confidence, 4)} below floor {cfg.confidence.floor} — playbook forced to stand-aside"
        )

    return Step1Output(
        meta=Meta(
            symbol=det.symbol, asset_class=cfg.universe.asset_class, timeframes=det.tfs,
            generated_at=_now_iso(),
            data_window=DataWindow(**{"from": cfg.data.history_start, "to": _ms_to_date(int(adf["timestamp"].iloc[-1]))}),
            engine_version=cfg.engine_version,
        ),
        regime=Regime(
            trend=trend,
            structure=D.structure_text(det.structure_1d),
            note=D.regime_note(det.ma_label, det.ma_vals, det.rsi_by_tf.get(det.anchor_tf), fcfg.rsi.oversold, fcfg.rsi.overbought),
        ),
        bias=conf.bias,
        levels=Levels(support=det.support, resistance=det.resistance, invalidation=inv),
        signals=signals, confluence_score=conf.score, confidence=conf.confidence, caveats=caveats,
        elliott=elliott, summaries=summaries, plan=plan,
    )


def deterministic(
    cfg: EngineConfig,
    symbol: str,
    candles: dict[str, pd.DataFrame],
    tfs: list[str],
) -> DetResult:
    """Pure deterministic Step 1 over an already-loaded candle set (no store, no LLM).

    `candles` maps each analysis TF -> its closed-candle DataFrame. This is the single
    source of truth for signals/confluence/bias; both `analyze` and the backtest call it.
    """
    anchor_tf = cfg.features.ma.anchor_tf
    fcfg = cfg.features

    # ---- per-TF features ----
    rsi_by_tf: dict[str, float] = {}
    structure_by_tf: dict[str, str] = {}
    pivots_by_tf: dict[str, list] = {}
    for tf in tfs:
        df = candles[tf]
        if df.empty:
            raise RuntimeError(f"no candles for {symbol} {tf}")
        rsi_by_tf[tf] = float(I.rsi(df["close"], fcfg.rsi.period).iloc[-1])
        piv = ST.find_pivots(df, fcfg.structure.pivot_lookback)
        pivots_by_tf[tf] = piv
        structure_by_tf[tf] = ST.classify_structure(piv, fcfg.structure.swing_count)

    # ---- anchor-TF features ----
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

    det = DetResult(
        cfg=cfg, symbol=symbol, tfs=tfs, anchor_tf=anchor_tf, candles=candles, adf=adf,
        close_last=close_last, atr_last=atr_last, ma_label=ma_label, ma_vals=ma_vals,
        vol_label=vol_label, price_dist=price_dist, support=support, resistance=resistance,
        anchor_pivots=anchor_pivots, rsi_by_tf=rsi_by_tf, structure_by_tf=structure_by_tf,
        structure_1d=structure_1d, signals=signals, conf=conf,
    )
    det.out = _build_output(det, conf, signals)  # deterministic (elliott/summaries/plan = null)
    return det


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
    candles: dict[str, pd.DataFrame] = {}
    for tf in tfs:
        df = S.read_candles(symbol, tf, root)
        if df.empty:
            raise RuntimeError(f"no stored candles for {symbol} {tf} — run a backfill first")
        candles[tf] = df

    det = deterministic(cfg, symbol, candles, tfs)
    out = det.out
    if not interpret:
        return out

    # ---- interpretive LLM layer (Step 1.5) ----
    from . import interpret as I_

    anchor_pivots = det.anchor_pivots

    def _recent(kind: str, n: int = 30) -> list[float]:
        return [round(p.price, 2) for p in anchor_pivots if p.kind == kind][-n:]

    def _pivot_series(n: int = 40) -> list[dict]:
        # full chronological pivot series (high/low) so the LLM can actually count waves
        return [
            {"t": _ms_to_date(p.timestamp), "kind": p.kind, "price": round(p.price, 2)}
            for p in anchor_pivots[-n:]
        ]

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
                "rsi": round(det.rsi_by_tf[tf], 2),
                "structure": det.structure_by_tf[tf],
                "last_close": round(float(det.candles[tf]["close"].iloc[-1]), 2),
            }
            for tf in tfs
        },
        "anchor_tf": det.anchor_tf,
        "ma_values": {k: round(v, 2) for k, v in det.ma_vals.items() if v == v},
        "atr": round(det.atr_last, 2),
        "vol_regime": det.vol_label,
        "pivot_series_1d": _pivot_series(),
        "recent_swing_highs_1d": _recent("high", 3),
        "recent_swing_lows_1d": _recent("low", 3),
        "caveats": out.caveats,
    }

    res = I_.interpret(out, digest, cfg, client=llm_client)

    # fold the single Elliott signal into confluence (ADR 0007 — low weight, supporting view)
    signals = det.signals
    conf = det.conf
    if cfg.elliott.weight and "elliott_1d" not in {s.name for s in signals}:
        signals = [*signals, Signal(name="elliott_1d", value=res.elliott_value, vote=res.elliott_vote, weight=cfg.elliott.weight)]
        conf = C.derive(signals, det.structure_by_tf, tfs, cfg)

    return _build_output(det, conf, signals, elliott=res.elliott, summaries=res.summaries, llm_plan=res.plan)


def analyze_default(symbol: str = "BTCUSDT", config_path: str = "config/engine.yaml", refresh: bool = False) -> Step1Output:
    return analyze(load_config(config_path), symbol, refresh=refresh)
