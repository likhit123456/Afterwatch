#!/usr/bin/env bash
# Offline rehearsal: start the vulnerable app, run the red-team gate against it,
# and show the verdict. On the vulnerable baseline this prints GATE: FAIL and the
# script exits 1 (as CI would). Run from anywhere:  bash demo/local-attack.sh
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8099}"
URL="http://127.0.0.1:${PORT}"
# Pick the first interpreter that actually runs (skips the Windows Store stub).
PY=""
for c in python python3 py; do
  if "$c" -c "import sys" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "no working python found"; exit 2; }

cd "$ROOT"
"$PY" -m uvicorn app.main:app --port "$PORT" --log-level warning &
APP_PID=$!
trap 'kill $APP_PID 2>/dev/null; wait $APP_PID 2>/dev/null' EXIT

echo "== starting app on $URL (pid $APP_PID) =="
for _ in $(seq 1 30); do
  if "$PY" -c "import urllib.request,sys; urllib.request.urlopen('$URL/health', timeout=1)" 2>/dev/null; then
    UP=1; break
  fi
  sleep 0.5
done
[ "${UP:-0}" = 1 ] || { echo "app did not come up on $URL"; exit 2; }
echo "== app is up =="
echo

"$PY" security/redteam.py --base-url "$URL"
RC=$?
echo
echo "redteam exit code: $RC  (non-zero blocks promotion in CI)"
exit $RC
