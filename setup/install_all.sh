#!/usr/bin/env bash
# Program: ult - install_all.sh
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Thin wrapper that checks python3 exists and hands off to the unified Python installer, passing along any arguments.
# ─────────────────────────────────────────────────────────────────────────────
# install_all.sh — The Sacred Tech setup wrapper for macOS and Linux
#
# Delegates configuration to the unified Python installer setup/install_all.py.
# ─────────────────────────────────────────────────────────────────────────────
# Stop on errors, unset variables and failed pipes.
set -euo pipefail

# Directory this script lives in, so the installer is found regardless of the caller's location.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verify python3 is installed
# Fail early if Python is missing.
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Please install Python 3.10+ first."
    exit 1
fi

# Replace this shell with the installer, forwarding all arguments.
exec python3 "$SCRIPT_DIR/install_all.py" "$@"
