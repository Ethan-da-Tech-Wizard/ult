#!/usr/bin/env bash
# Launches The Sacred Tech. Self-bootstrapping: if the Python dependencies
# are missing, they are installed into a local .venv automatically, so a
# fresh download plays with this one command.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Install Python 3.10+ (see README.md) and retry."
    exit 1
fi

PY="python3"
if [[ -x ".venv/bin/python" ]] && .venv/bin/python -c "import fastapi, uvicorn, numpy" >/dev/null 2>&1; then
    PY=".venv/bin/python"
elif ! python3 -c "import fastapi, uvicorn, numpy" >/dev/null 2>&1; then
    echo "[bootstrap] First launch: installing game dependencies into .venv ..."
    if [[ ! -d ".venv" ]]; then
        python3 -m venv .venv
    fi
    .venv/bin/python -m pip install --quiet --upgrade pip
    .venv/bin/python -m pip install --quiet -r requirements.txt
    PY=".venv/bin/python"
    echo "[bootstrap] Done."
fi

echo ""
echo "▶️   The Sacred Tech is starting..."
echo "    Open http://127.0.0.1:8000 in your browser."
echo ""
exec "$PY" server/main.py
