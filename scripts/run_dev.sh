#!/usr/bin/env bash
# Program: ult - run_dev.sh
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Launcher that installs missing Python dependencies into a local .venv on first run, prints setup notes for the optional sandbox and VM, then starts the game server.
# Launches The Sacred Tech. Self-bootstrapping: if the Python dependencies
# are missing, they are installed into a local .venv automatically, so a
# fresh download plays with this one command.
# Stop on errors, unset variables and failed pipes.
set -euo pipefail

# Resolve the repository root (one level above this script) so it works from any directory.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Fail early with a clear message if Python is missing.
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Install Python 3.10+ (see README.md) and retry."
    exit 1
fi

# Choose the interpreter: the existing .venv if it already has the packages, else system Python if it has them, else create .venv and install requirements.
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
# Notice about the optional Docker sandbox and QEMU VM.
echo "=========================================================="
echo " ⚠️  SYSTEM REQUIREMENTS & SETUP NOTICE:"
echo " Core game only requires Python (running now)."
echo " To enable optional Arch Sandbox (T2) & TempleOS VM (T3):"
echo "   - Make sure Docker & QEMU are installed on your host."
echo "   - Run: python setup/install_all.py to build them."
echo "   - If missing, the game falls back to host execution."
echo "=========================================================="
echo ""
echo "▶️   The Sacred Tech is starting..."
echo "    Open http://127.0.0.1:8000 in your browser."
echo ""
# Replace this shell with the server process.
exec "$PY" server/main.py
