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

    if o.plan is not None:
        p = o.plan
        lines += [
            "", "## Plan (LLM)",
            f"- playbook: **{p.playbook}**",
            f"- entry {p.entry_zone} · stop {p.stop} · targets {p.targets} · R:R {p.r_r}",
            f"- sizing: {p.sizing_note}",
            f"- note: {p.note}",
        ]
    if o.summaries is not None:
        s = o.summaries
        lines += ["", "## Summaries (LLM)",
                  f"- **daily**: {s.daily}", f"- **weekly**: {s.weekly}", f"- **monthly**: {s.monthly}"]
    if o.elliott is not None and o.elliott.tf_1d is not None:
        e = o.elliott.tf_1d
        lines += ["", "## Elliott 1d (LLM — supporting view)",
                  f"- {e.current_wave} · {e.structure} → {e.implied_direction} (conf {e.confidence})",
                  f"- primary: {e.primary_count}", f"- alt: {e.alt_count}"]

    interp = [k for k, v in (("elliott", o.elliott), ("summaries", o.summaries), ("plan", o.plan)) if v is None]
    if interp:
        lines += ["", f"> interpretive blocks null (deterministic only): {', '.join(interp)}"]
    return "\n".join(lines) + "\n"
