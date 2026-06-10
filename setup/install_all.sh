#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# install_all.sh — The Sacred Tech setup wrapper for macOS and Linux
#
# Delegates configuration to the unified Python installer setup/install_all.py.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verify python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Please install Python 3.10+ first."
    exit 1
fi

exec python3 "$SCRIPT_DIR/install_all.py" "$@"
