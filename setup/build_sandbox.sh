#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build_sandbox.sh
# Builds the Arch Linux zeus-arch Docker image for the Sacred Tech sandbox.
# Run once before starting the game server.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SANDBOX_DIR="$PROJECT_ROOT/sandbox"
IMAGE_NAME="zeus-arch:latest"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   The Sacred Tech — Arch Linux Sandbox Builder       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check Docker is installed
if ! command -v docker &>/dev/null; then
    echo "❌  Docker is not installed. Please install Docker Desktop first."
    echo "    → https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker daemon is running
if ! docker info &>/dev/null 2>&1; then
    echo "❌  Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅  Docker found: $(docker --version)"
echo ""

# Check if image already exists
if docker image inspect "$IMAGE_NAME" &>/dev/null 2>&1; then
    echo "ℹ️   Image '$IMAGE_NAME' already exists."
    read -r -p "    Rebuild? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping build. Using existing image."
        exit 0
    fi
    docker rmi "$IMAGE_NAME" || true
fi

echo "🏗️   Building $IMAGE_NAME from $SANDBOX_DIR/Dockerfile ..."
echo ""

docker build \
    --tag "$IMAGE_NAME" \
    --file "$SANDBOX_DIR/Dockerfile" \
    "$SANDBOX_DIR"

echo ""
echo "✅  Build complete: $IMAGE_NAME"
echo ""
echo "To start the sandbox container manually:"
echo "  docker run -d --name zeus-sandbox \\"
echo "    -v \"\$PWD/save_data/relic_save:/workspace\" \\"
echo "    -v \"\$PWD/sandbox:/sandbox\" \\"
echo "    -w /workspace zeus-arch:latest tail -f /dev/null"
echo ""
echo "The game server (python server/main.py) will auto-start and"
echo "auto-connect to this container when you compile code in the editor."
echo ""
