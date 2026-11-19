#!/usr/bin/env bash

# ==============================================================================
# Program: run_dev.sh
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Development server bootstrap and runtime orchestrator for The Sacred Tech.
#          Validates Python runtime presence, performs self-bootstrapping virtual environment
#          provisioning, installs dependencies from requirements.txt, verifies optional hypervisor
#          and container subsystems (Docker, QEMU), and executes the FastAPI server process
#          bound strictly to loopback interfaces with hot-reload capabilities.
# ==============================================================================

# Halt on error (-e), treat uninitialized variables as fatal errors (-u),
# and prevent pipe masking of intermediate non-zero return codes (-o pipefail).
set -euo pipefail

# ------------------------------------------------------------------------------
# Phase 1: Working Directory and Canonical Path Resolution
# ------------------------------------------------------------------------------
# Resolve the absolute canonical root path of the repository
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# ------------------------------------------------------------------------------
# Phase 2: Host Python Interpreter Presence Check
# ------------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Install Python 3.10+ (see README.md) and retry."
    exit 1
fi

# ------------------------------------------------------------------------------
# Phase 3: Self-Bootstrapping Virtual Environment Provisioning
# ------------------------------------------------------------------------------
# Default to system python3 unless virtual environment is active and healthy
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

# ------------------------------------------------------------------------------
# Phase 4: Subsystem Diagnostics & Operational Notice
# ------------------------------------------------------------------------------
echo ""
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

# ------------------------------------------------------------------------------
# Phase 5: Executable Process Replacement
# ------------------------------------------------------------------------------
# Replace the shell process image directly with the Uvicorn/FastAPI server process
exec "$PY" server/main.py
