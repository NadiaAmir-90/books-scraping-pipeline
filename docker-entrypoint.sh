#!/bin/sh
set -e
scrapyd &
python - <<'PY'
import time, urllib.request
for _ in range(60):
    try:
        urllib.request.urlopen("http://localhost:6800/daemonstatus.json")
        break
    except Exception:
        time.sleep(1)
PY
cd /app/books_scraper && scrapyd-deploy
wait
