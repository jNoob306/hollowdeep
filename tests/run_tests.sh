#!/usr/bin/env bash
# Headless logic tests (no GPU needed). Requires: python3, playwright (pip install playwright && playwright install chromium)
# Optional: CHROME=/path/to/chrome to use a system Chrome instead of Playwright's Chromium.
set -e
cd "$(dirname "$0")"
python3 make_stub.py
node --check build/game.mjs && echo "syntax OK"
export PORT=${PORT:-8765}
python3 -m http.server "$PORT" --directory build >/dev/null 2>&1 &
SERVER=$!; trap "kill $SERVER" EXIT; sleep 1
echo "== smoke test =="; python3 smoke_test.py
echo "== maze + Bellman test =="; python3 bellman_test.py
