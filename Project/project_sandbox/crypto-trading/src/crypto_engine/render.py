"""Render a Step1Output as a human-readable markdown summary (Step 2 review)."""

from __future__ import annotations

from .contract import Step1Output


def to_markdown(o: Step1Output) -> str:
    m, b, r, lv, cs = o.meta, o.bias, o.regime, o.levels, o.confluence_score
    lines = [
        f"# {m.symbol} — Step 1 analysis ({m.asset_class})",
        f"_generated {m.generated_at} · engine {m.engine_version} · TFs {', '.join(m.timeframes)}_",
        f"_data {m.data_window.from_} → {m.data_window.to}_",
        "",
        f"## Bias: **{b.direction.upper()}** ({b.conviction}) · confidence {o.confidence}",
        f"- regime: **{r.trend}** — {r.structure} ({r.note})",
        "- TF alignment: " + ", ".join(f"{tf}={d}" for tf, d in b.timeframe_alignment.items()),
        f"- confluence: long {cs.long} · short {cs.short} · neutral {cs.neutral}",
        "",
        "## Signals",
        "| signal | value | vote | weight |",
        "|---|---|---|---|",
    ]
    for s in o.signals:
        lines.append(f"| {s.name} | {s.value} | {s.vote} | {s.weight} |")
    lines += [
        "",
        "## Levels",
        f"- support: {lv.support}",
        f"- resistance: {lv.resistance}",
        f"- invalidation: {lv.invalidation.price} — {lv.invalidation.rule}",
        "",
        "## Caveats",
    ]
    lines += [f"- {c}" for c in o.caveats]
    interp = [k for k, v in (("elliott", o.elliott), ("summaries", o.summaries), ("plan", o.plan)) if v is None]
    if interp:
        lines += ["", f"> interpretive blocks null (v1 deterministic): {', '.join(interp)}"]
    return "\n".join(lines) + "\n"
