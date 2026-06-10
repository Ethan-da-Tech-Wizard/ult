#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# install_all.sh — The Sacred Tech one-file installer
#
# Installs everything the game needs in one run:
#   Tier 1 (required): Python venv + all packages from requirements.txt
#   Tier 2 (optional): Arch Linux Docker sandbox image + container
#   Tier 3 (optional): TempleOS Altar QEMU VM image
#
# Usage:
#   ./setup/install_all.sh            interactive (asks before optional tiers)
#   ./setup/install_all.sh --minimal  Tier 1 only, no prompts
#   ./setup/install_all.sh --full     every tier the machine supports, no prompts
#
# Safe to re-run: every step checks what already exists.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
MODE="interactive"

case "${1:-}" in
    --minimal) MODE="minimal" ;;
    --full)    MODE="full" ;;
    "")        ;;
    *) echo "Unknown option: $1 (use --minimal or --full)"; exit 1 ;;
esac

TIER1_STATUS="not installed"
TIER2_STATUS="skipped"
TIER3_STATUS="skipped"

ask() {
    # ask "question" -> 0 yes / 1 no, honoring --minimal/--full
    case "$MODE" in
        minimal) return 1 ;;
        full)    return 0 ;;
    esac
    read -r -p "$1 [y/N] " response
    [[ "$response" =~ ^[Yy]$ ]]
}

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   The Sacred Tech — One-File Installer                   ║"
echo "╚══════════════════════════════════════════════════════════╝"

# ── Tier 1: Python core (required) ──────────────────────────────────────────
echo ""
echo "── Tier 1: Core game (Python) ─────────────────────────────"

if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Install Python 3.10+ first:"
    echo "    macOS:  brew install python3"
    echo "    Linux:  sudo apt install python3 python3-venv python3-pip"
    echo "    Windows: https://www.python.org/downloads/ (then see README Windows notes)"
    exit 1
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "❌  Python $PY_VERSION found, but 3.10+ is required."
    exit 1
fi
echo "✅  Python $PY_VERSION"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "📦  Creating virtual environment at .venv ..."
    python3 -m venv "$VENV_DIR"
fi

echo "📦  Installing Python packages from requirements.txt ..."
"$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
"$VENV_DIR/bin/python" -m pip install --quiet -r "$PROJECT_ROOT/requirements.txt"
echo "✅  Core game dependencies installed."
TIER1_STATUS="installed (.venv)"

# ── Tier 2: Arch Linux Docker sandbox (optional) ────────────────────────────
echo ""
echo "── Tier 2: Arch Linux sandbox (Docker) ────────────────────"

if ! command -v docker &>/dev/null; then
    echo "ℹ️   Docker not found — skipping. The in-game terminal will use your"
    echo "    host shell, and validators run locally. Install Docker Desktop"
    echo "    and re-run this script to enable the real Arch sandbox."
    TIER2_STATUS="skipped (Docker not installed)"
elif ! docker info &>/dev/null 2>&1; then
    echo "ℹ️   Docker is installed but the daemon isn't running — skipping."
    echo "    Start Docker and re-run this script to enable the sandbox."
    TIER2_STATUS="skipped (Docker daemon not running)"
elif ask "Build the Arch Linux sandbox image (~1 GB download)?"; then
    if docker image inspect zeus-arch:latest &>/dev/null 2>&1; then
        echo "✅  Image zeus-arch:latest already built."
    else
        echo "🏗️   Building zeus-arch:latest (this downloads Arch packages) ..."
        docker build --tag zeus-arch:latest \
            --file "$PROJECT_ROOT/sandbox/Dockerfile" "$PROJECT_ROOT/sandbox"
    fi

    mkdir -p "$PROJECT_ROOT/save_data/relic_save"
    if [[ -n "$(docker ps --filter name=zeus-sandbox -q)" ]]; then
        echo "✅  Container zeus-sandbox already running."
    elif [[ -n "$(docker ps -a --filter name=zeus-sandbox -q)" ]]; then
        echo "▶️   Starting existing zeus-sandbox container ..."
        docker start zeus-sandbox >/dev/null
    else
        echo "▶️   Launching zeus-sandbox container ..."
        docker run -d --name zeus-sandbox \
            -v "$PROJECT_ROOT/save_data/relic_save:/workspace" \
            -v "$PROJECT_ROOT/sandbox:/sandbox" \
            -w /workspace zeus-arch:latest tail -f /dev/null >/dev/null
    fi
    echo "✅  Arch Linux sandbox ready."
    TIER2_STATUS="installed and running"
else
    TIER2_STATUS="skipped (declined)"
fi

# ── Tier 3: TempleOS Altar VM (optional) ────────────────────────────────────
echo ""
echo "── Tier 3: TempleOS Altar VM (QEMU) ───────────────────────"

if ! command -v qemu-system-x86_64 &>/dev/null; then
    echo "ℹ️   QEMU not found — skipping. Chapter 21 will use the built-in"
    echo "    validating HolyC altar (same puzzles, no VM). Install QEMU"
    echo "    (brew install qemu / apt install qemu-system-x86 qemu-utils)"
    echo "    and re-run to enable the real TempleOS VM."
    TIER3_STATUS="skipped (QEMU not installed)"
elif [[ -f "$PROJECT_ROOT/save_data/templeos_core.img" ]]; then
    echo "✅  TempleOS image already built."
    TIER3_STATUS="already built"
elif [[ "$MODE" == "full" || "$MODE" == "interactive" ]] && ask "Build the TempleOS VM image now? (downloads the ISO and opens a one-time interactive installer window)"; then
    "$SCRIPT_DIR/build_templeos_img.sh"
    TIER3_STATUS="installed"
else
    echo "ℹ️   Skipped. Run setup/build_templeos_img.sh later if you want the VM."
    TIER3_STATUS="skipped"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Installation summary                                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  Tier 1 — Core game:        $TIER1_STATUS"
echo "  Tier 2 — Arch sandbox:     $TIER2_STATUS"
echo "  Tier 3 — TempleOS VM:      $TIER3_STATUS"
echo ""
echo "▶️   Play now:"
echo "      ./scripts/run_dev.sh"
echo "      then open http://127.0.0.1:8000"
echo ""
