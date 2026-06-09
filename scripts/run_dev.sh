#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! python3 -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    echo "Missing Python server dependencies."
    echo "Run: python3 -m pip install -r requirements.txt"
    exit 1
fi

python3 server/main.py
