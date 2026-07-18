"""Aggregate replay rows into a forward-return distribution per bias/conviction
bucket, render a JSON + markdown report, and answer the honest question.

Percentages/returns are stored as fractions (0.0123 = +1.23%) and formatted on render.
"""

from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

from ..config import EngineConfig
from ..data import store as S
from .replay import ReplayRow, replay_from_store

BIASES = ["long", "short", "neutral"]
CONVICTIONS = ["low", "medium", "high"]


# ---------- contract ----------
class BucketStat(BaseModel):
    horizon: str
    n: int
    mean_return: float
    median_return: float
    std_return: float
    pct_positive: float
    directional_hit_rate: Optional[float] = None  # aligned to bias; None for neutral/baseline


class Bucket(BaseModel):
    label: str
    bias: Optional[str] = None
    conviction: Optional[str] = None
    n_signals: int
    stats: list[BucketStat]


class BacktestVerdict(BaseModel):
    question: str
    short_bias_mean_by_horizon: dict[str, Optional[float]]
    short_bias_negative_by_horizon: dict[str, Optional[bool]]
    long_bias_mean_by_horizon: dict[str, Optional[float]]
    long_bias_positive_by_horizon: dict[str, Optional[bool]]
    verdict: str


class BacktestReport(BaseModel):
    symbol: str
    anchor_tf: str
    horizons_bars: list[int]
    horizon_labels: list[str]
    n_bars_evaluated: int
    data_window: dict[str, str]
    generated_at: str
    buckets: list[Bucket]
    verdict: BacktestVerdict

    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(**kwargs)


# ---------- aggregation ----------
def _stat(label: str, returns: list[float], align: Optional[str]) -> BucketStat:
    if not returns:
        return BucketStat(horizon=label, n=0, mean_return=0.0, median_return=0.0,
                          std_return=0.0, pct_positive=0.0, directional_hit_rate=None)
    n = len(returns)
    pos = sum(1 for r in returns if r > 0)
    hit: Optional[float] = None
    if align == "long":
        hit = round(sum(1 for r in returns if r > 0) / n, 4)
    elif align == "short":
        hit = round(sum(1 for r in returns if r < 0) / n, 4)
    return BucketStat(
        horizon=label, n=n,
        mean_return=round(statistics.fmean(returns), 6),
        median_return=round(statistics.median(returns), 6),
        std_return=round(statistics.pstdev(returns), 6) if n > 1 else 0.0,
        pct_positive=round(pos / n, 4),
        directional_hit_rate=hit,
    )


def _bucket(label: str, rows: list[ReplayRow], labels: list[str],
            bias: Optional[str], conviction: Optional[str], align: Optional[str]) -> Bucket:
    stats = []
    for lab in labels:
        rets = [r.forward[lab] for r in rows if r.forward.get(lab) is not None]
        stats.append(_stat(lab, [x for x in rets if x is not None], align))
    return Bucket(label=label, bias=bias, conviction=conviction, n_signals=len(rows), stats=stats)


def aggregate(rows: list[ReplayRow], horizon_labels: list[str], horizons_bars: list[int],
              symbol: str, anchor_tf: str) -> BacktestReport:
    buckets: list[Bucket] = [_bucket("baseline (all bars)", rows, horizon_labels, None, None, None)]

    per_bias: dict[str, list[ReplayRow]] = {b: [r for r in rows if r.bias == b] for b in BIASES}
    for b in BIASES:
        align = b if b in ("long", "short") else None
        buckets.append(_bucket(b, per_bias[b], horizon_labels, b, None, align))
        for c in CONVICTIONS:
            sub = [r for r in per_bias[b] if r.conviction == c]
            if sub:
                buckets.append(_bucket(f"{b}/{c}", sub, horizon_labels, b, c, align))

    # verdict: short-bias should be negative, long-bias positive
    short_rows = per_bias["short"]
    long_rows = per_bias["long"]

    def _mean(rows_: list[ReplayRow], lab: str) -> Optional[float]:
        vals = [r.forward[lab] for r in rows_ if r.forward.get(lab) is not None]
        return round(statistics.fmean([v for v in vals if v is not None]), 6) if vals else None

    short_mean = {lab: _mean(short_rows, lab) for lab in horizon_labels}
    long_mean = {lab: _mean(long_rows, lab) for lab in horizon_labels}
    short_neg = {lab: (v < 0 if v is not None else None) for lab, v in short_mean.items()}
    long_pos = {lab: (v > 0 if v is not None else None) for lab, v in long_mean.items()}

    short_ok = [short_neg[lab] for lab in horizon_labels if short_neg[lab] is not None]
    long_ok = [long_pos[lab] for lab in horizon_labels if long_pos[lab] is not None]
    n_short_ok = sum(1 for x in short_ok if x)
    n_long_ok = sum(1 for x in long_ok if x)

    if not short_rows and not long_rows:
        verdict = "INCONCLUSIVE — no directional (long/short) signals were produced over this window."
    else:
        parts = []
        if short_rows:
            parts.append(
                f"short-bias forward return negative in {n_short_ok}/{len(short_ok)} horizons "
                f"(n={len(short_rows)} signals)"
            )
        if long_rows:
            parts.append(
                f"long-bias forward return positive in {n_long_ok}/{len(long_ok)} horizons "
                f"(n={len(long_rows)} signals)"
            )
        directional_pass = (not short_ok or n_short_ok == len(short_ok)) and (
            not long_ok or n_long_ok == len(long_ok)
        )
        head = "EDGE CONSISTENT WITH BIAS" if directional_pass else "EDGE NOT CONSISTENT — retune or distrust weights"
        verdict = head + " — " + "; ".join(parts) + "."

    return BacktestReport(
        symbol=symbol, anchor_tf=anchor_tf, horizons_bars=horizons_bars,
        horizon_labels=horizon_labels,
        n_bars_evaluated=len(rows),
        data_window={
            "from": rows[0].date if rows else "",
            "to": rows[-1].date if rows else "",
        },
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        buckets=buckets,
        verdict=BacktestVerdict(
            question="Do short-bias signals show negative forward returns (and long-bias positive)?",
            short_bias_mean_by_horizon=short_mean,
            short_bias_negative_by_horizon=short_neg,
            long_bias_mean_by_horizon=long_mean,
            long_bias_positive_by_horizon=long_pos,
            verdict=verdict,
        ),
    )


# ---------- render ----------
def _pct(x: float) -> str:
    return f"{x * 100:+.2f}%"


def to_markdown(rep: BacktestReport) -> str:
    L = [
        f"# {rep.symbol} — backtest (forward-return by bias)",
        f"_generated {rep.generated_at} · anchor {rep.anchor_tf} · "
        f"{rep.n_bars_evaluated} closes replayed · {rep.data_window.get('from')} → {rep.data_window.get('to')}_",
        f"_horizons (anchor bars): {', '.join(rep.horizon_labels)}_",
        "",
        "## Verdict",
        f"**{rep.verdict.verdict}**",
        "",
        f"> {rep.verdict.question}",
        "",
        "| horizon | short-bias mean | negative? | long-bias mean | positive? |",
        "|---|---|---|---|---|",
    ]
    for lab in rep.horizon_labels:
        sm = rep.verdict.short_bias_mean_by_horizon.get(lab)
        lm = rep.verdict.long_bias_mean_by_horizon.get(lab)
        sn = rep.verdict.short_bias_negative_by_horizon.get(lab)
        lp = rep.verdict.long_bias_positive_by_horizon.get(lab)
        L.append(
            f"| {lab} | {_pct(sm) if sm is not None else '—'} | {'yes' if sn else ('no' if sn is not None else '—')} "
            f"| {_pct(lm) if lm is not None else '—'} | {'yes' if lp else ('no' if lp is not None else '—')} |"
        )

    L += ["", "## Distribution by bucket"]
    for bk in rep.buckets:
        L += [
            "",
            f"### {bk.label} — {bk.n_signals} signals",
            "| horizon | n | mean | median | std | % positive | dir. hit-rate |",
            "|---|---|---|---|---|---|---|",
        ]
        for st in bk.stats:
            hit = f"{st.directional_hit_rate * 100:.1f}%" if st.directional_hit_rate is not None else "—"
            L.append(
                f"| {st.horizon} | {st.n} | {_pct(st.mean_return)} | {_pct(st.median_return)} "
                f"| {_pct(st.std_return)} | {st.pct_positive * 100:.1f}% | {hit} |"
            )

    L += [
        "",
        "---",
        "_Forward returns are realised close-to-close over the anchor timeframe; "
        "no fees/slippage/leverage. Directional hit-rate = fraction of signals whose "
        "realised move matched the bias (short→down, long→up). This is a signal-quality "
        "probe, not a P&L backtest — not investment advice._",
    ]
    return "\n".join(L) + "\n"


# ---------- orchestration ----------
def run_backtest(
    cfg: EngineConfig,
    symbol: str,
    root: str = S.DEFAULT_ROOT,
    *,
    limit: int = 0,
    stride: int = 1,
) -> BacktestReport:
    rows, labels = replay_from_store(cfg, symbol, root, limit=limit, stride=stride)
    return aggregate(rows, labels, cfg.backtest.horizons, symbol, cfg.features.ma.anchor_tf)
