"""CLI — `crypto-engine analyze` / `backfill` (Step 1, manual run)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from .config import load_config
from .data import backfill as B
from .engine import analyze
from .pine import to_pine
from .render import to_markdown

app = typer.Typer(add_completion=False, help="Crypto trading decision-support engine (Step 1)")
journal_app = typer.Typer(add_completion=False, help="Append-only trade journal + monthly plan-vs-actual review")
app.add_typer(journal_app, name="journal")
console = Console()


def _parse_tfs(tf: str | None) -> list[str] | None:
    if not tf:
        return None
    return [t.strip() for t in tf.split(",") if t.strip()]


@app.command()
def backfill(
    symbol: str = typer.Option("BTCUSDT", "--symbol", "-s"),
    config: str = typer.Option("config/engine.yaml", "--config", "-c"),
):
    """Fetch + store candle history (all configured timeframes)."""
    cfg = load_config(config)
    for r in B.backfill_symbol(cfg, symbol):
        console.print(f"[green]{r.timeframe:>3}[/] fetched {r.fetched} · stored {r.stored_total}")


def analyze_cmd(
    symbol: str = typer.Option("BTCUSDT", "--symbol", "-s"),
    tf: str = typer.Option(None, "--tf", help="override timeframes, e.g. 1h,4h,1d"),
    config: str = typer.Option("config/engine.yaml", "--config", "-c"),
    refresh: bool = typer.Option(False, "--refresh", help="backfill before analyzing"),
    interpret: bool = typer.Option(False, "--interpret", help="run the LLM layer (Elliott/summaries/plan); needs ANTHROPIC_API_KEY"),
    pine: bool = typer.Option(False, "--pine", help="also emit a Pine Script v6 overlay to paste into TradingView"),
    notify: bool = typer.Option(False, "--notify", help="push a one-line summary (Telegram if env set, else macOS notification)"),
):
    """Run Step 1 analysis -> JSON + markdown artifact in output/."""
    cfg = load_config(config)
    tfs = _parse_tfs(tf)
    if tfs:
        cfg.universe.timeframes = tfs

    out = analyze(cfg, symbol, refresh=refresh, interpret=interpret)

    out_dir = Path(cfg.output.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"{symbol}_{stamp}.json"
    json_path.write_text(out.to_json(indent=2), encoding="utf-8")
    if cfg.output.write_markdown:
        (out_dir / f"{symbol}_{stamp}.md").write_text(to_markdown(out), encoding="utf-8")
    if pine:
        pine_path = out_dir / f"{symbol}_{stamp}.pine"
        pine_path.write_text(to_pine(out), encoding="utf-8")

    console.print(to_markdown(out))
    console.print(f"[dim]written: {json_path}{' + .pine' if pine else ''}[/]")

    if notify:
        from . import notify as N

        channel = N.send(N.build_message(out), title=f"crypto-engine {symbol}")
        console.print(f"[dim]notify: {channel}[/]")


# expose `analyze` as the subcommand name (not analyze_cmd)
app.command(name="analyze")(analyze_cmd)


@app.command()
def backtest(
    symbol: str = typer.Option("BTCUSDT", "--symbol", "-s"),
    config: str = typer.Option("config/engine.yaml", "--config", "-c"),
    limit: int = typer.Option(0, "--limit", help="evaluate only the most-recent N anchor closes (0 = all)"),
    stride: int = typer.Option(1, "--stride", help="evaluate every K-th anchor close (speed vs resolution)"),
):
    """Replay stored candles -> forward-return distribution per bias/conviction bucket.

    Writes output/backtest_report.json + .md. Answers: do short-bias signals actually
    show negative forward returns?
    """
    from .backtest import run_backtest, to_markdown as bt_md

    cfg = load_config(config)
    rep = run_backtest(cfg, symbol, limit=limit, stride=stride)

    out_dir = Path(cfg.output.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "backtest_report.json").write_text(rep.to_json(indent=2), encoding="utf-8")
    (out_dir / "backtest_report.md").write_text(bt_md(rep), encoding="utf-8")

    console.print(bt_md(rep))
    console.print(f"[dim]written: {out_dir / 'backtest_report.json'} + .md[/]")


@journal_app.command("log")
def journal_log(
    artifact: str = typer.Option(..., "--artifact", "-a", help="analyze artifact id, e.g. BTCUSDT_20260607T121226Z"),
    action: str = typer.Option(..., "--action", help="long | short | close | skip"),
    symbol: str = typer.Option("BTCUSDT", "--symbol", "-s"),
    entry: float = typer.Option(None, "--entry"),
    exit_: float = typer.Option(None, "--exit"),
    stop: float = typer.Option(None, "--stop"),
    size: float = typer.Option(None, "--size"),
    r: float = typer.Option(None, "--r", help="realised R; computed from entry/exit/stop if omitted"),
    planned_bias: str = typer.Option(None, "--planned-bias", help="engine bias at the time (for plan-vs-actual)"),
    planned_playbook: str = typer.Option(None, "--planned-playbook"),
    note: str = typer.Option(None, "--note"),
    config: str = typer.Option("config/engine.yaml", "--config", "-c"),
):
    """Append a taken trade to the append-only journal (output/journal.jsonl)."""
    from . import journal as J

    cfg = load_config(config)
    computed_r = r
    if computed_r is None and entry is not None and exit_ is not None and stop is not None:
        computed_r = J.compute_r(action, entry, exit_, stop)
    e = J.JournalEntry(
        artifact_id=artifact, symbol=symbol, action=action, entry=entry, exit=exit_,
        stop=stop, size=size, r=computed_r, planned_bias=planned_bias,
        planned_playbook=planned_playbook, note=note,
    )
    path = J.append_entry(e, J.default_path(cfg.output.dir))
    rtxt = f" · {computed_r:+.2f}R" if computed_r is not None else ""
    console.print(f"[green]logged[/] {action} {symbol}{rtxt} -> {path}")


@journal_app.command("summary")
def journal_summary(
    month: str = typer.Option(None, "--month", "-m", help="YYYY-MM (default: all entries)"),
    config: str = typer.Option("config/engine.yaml", "--config", "-c"),
):
    """Monthly plan-vs-actual review from the journal."""
    from . import journal as J

    cfg = load_config(config)
    entries = J.read_entries(J.default_path(cfg.output.dir))
    console.print(J.summary_markdown(J.monthly_summary(entries, month)))


if __name__ == "__main__":
    app()
