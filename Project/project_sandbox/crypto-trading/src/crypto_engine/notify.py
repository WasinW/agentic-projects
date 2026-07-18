"""Notification sink for the daily job — Telegram -> macOS desktop -> silent artifact.

Channel selection (no tokens are ever hardcoded — all read from the environment):
  1. Telegram   if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set
  2. macOS      desktop notification via osascript (on darwin)
  3. none       just rely on the output/ artifact that was already written

Uses stdlib urllib (no new dependency). `choose_channel` is pure so the routing is
unit-testable without a network or tokens.
"""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.parse
import urllib.request

from .contract import Step1Output


def build_message(o: Step1Output) -> str:
    b = o.bias
    pb = o.plan.playbook if o.plan else "—"
    return (
        f"{o.meta.symbol} {b.direction.upper()} ({b.conviction}) "
        f"conf {o.confidence} · {pb} · inv {o.levels.invalidation.price}"
    )


def choose_channel(env: dict | None = None) -> str:
    env = env if env is not None else os.environ
    if env.get("TELEGRAM_BOT_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        return "telegram"
    if env.get("CE_NO_DESKTOP_NOTIFY"):
        return "none"
    if sys.platform == "darwin":
        return "macos"
    return "none"


def _send_telegram(message: str, env: dict, timeout: float = 10.0) -> None:
    token = env["TELEGRAM_BOT_TOKEN"]
    chat_id = env["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=timeout):  # noqa: S310 (fixed api.telegram.org host)
        pass


def _send_macos(message: str, title: str) -> None:
    safe = message.replace('"', "'")
    safe_title = title.replace('"', "'")
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe}" with title "{safe_title}"'],
        check=False,
    )


def send(message: str, title: str = "crypto-engine", env: dict | None = None) -> str:
    """Send `message` over the best available channel. Returns the channel actually used
    ('telegram' | 'macos' | 'none', or '<channel>-failed' if the send raised)."""
    env = env if env is not None else os.environ
    channel = choose_channel(env)
    try:
        if channel == "telegram":
            _send_telegram(message, env)
        elif channel == "macos":
            _send_macos(message, title)
    except Exception:  # never let a notification failure crash the daily job
        return f"{channel}-failed"
    return channel
