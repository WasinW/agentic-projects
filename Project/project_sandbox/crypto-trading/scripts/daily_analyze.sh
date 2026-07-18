#!/usr/bin/env bash
#
# Daily crypto-engine analyze + notification — the launchd/cron entry point.
#
# Notification (handled inside `analyze --notify`, see src/crypto_engine/notify.py):
#   * Telegram  if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are exported
#   * macOS     desktop notification otherwise (on this Mac)
#   * silent    otherwise — the output/ artifact is still written
#
# NO tokens are stored in this file. Export them in your shell env or in the
# launchd plist's <EnvironmentVariables> (see README "Automation").
#
# Env overrides: CE_SYMBOL (default BTCUSDT), CE_TFS (default 1h,4h,1d),
#                CE_INTERPRET=1 to also run the LLM layer (needs ANTHROPIC_API_KEY).

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

PY="$REPO/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

SYMBOL="${CE_SYMBOL:-BTCUSDT}"
TFS="${CE_TFS:-1h,4h,1d}"
LOG="$REPO/output/daily_analyze.log"
mkdir -p "$REPO/output"

EXTRA=()
[ "${CE_INTERPRET:-0}" = "1" ] && EXTRA+=(--interpret)

run() {
  # ${EXTRA[@]+...} keeps this safe under `set -u` on macOS bash 3.2 when EXTRA is empty
  PYTHONPATH="$REPO/src" "$PY" -m crypto_engine.cli analyze \
    --symbol "$SYMBOL" --tf "$TFS" --notify "$@" ${EXTRA[@]+"${EXTRA[@]}"}
}

echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) daily analyze $SYMBOL [$TFS] ===" >> "$LOG"

# Prefer fresh candles; if the fetch fails (offline / exchange hiccup) fall back
# to stored candles so the job still produces an artifact + notification.
if run --refresh >> "$LOG" 2>&1; then
  echo "ok (refreshed)" >> "$LOG"
else
  echo "refresh failed — analyzing on stored candles" >> "$LOG"
  run >> "$LOG" 2>&1 && echo "ok (stored)" >> "$LOG" || echo "FAILED" >> "$LOG"
fi
