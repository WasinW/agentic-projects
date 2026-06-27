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


# expose `analyze` as the subcommand name (not analyze_cmd)
app.command(name="analyze")(analyze_cmd)


if __name__ == "__main__":
    app()
