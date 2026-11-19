#!/usr/bin/env bash

# ==============================================================================
# Program: build_sandbox.sh
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Docker container image builder for The Sacred Tech's Arch Linux execution sandbox.
#          Verifies host Docker installation and daemon connectivity, checks for pre-existing
#          image tags, prompts for optional rebuilds, and executes container builds from Dockerfile
#          configuring the isolated environment for executing code challenges.
# ==============================================================================

# How this file fits the app: stand-alone way to build the Docker image the sandbox runs in (also done by setup/install_all.py). The image zeus-arch:latest (from sandbox/Dockerfile) is what server/sandbox_manager.py starts as container "zeus-sandbox". The IMAGE_NAME here must match the tag used in sandbox_manager.py and install_all.py.
# Halt on error (-e), treat uninitialized variables as fatal errors (-u),
# and prevent pipe masking of intermediate non-zero return codes (-o pipefail).
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

# Docker has to be installed and its daemon running; otherwise stop with a friendly message (both checks use exit code 1).
# ------------------------------------------------------------------------------
# Pre-Flight Checks: Docker Engine and Daemon Availability
# ------------------------------------------------------------------------------
if ! command -v docker &>/dev/null; then
    echo "❌  Docker is not installed. Please install Docker Desktop first."
    echo "    → https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &>/dev/null 2>&1; then
    echo "❌  Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅  Docker found: $(docker --version)"
echo ""

# Rebuilds are opt-in because a build downloads about 1 GB; `docker rmi ... || true` ignores a failure (for example when a container still uses the image, in which case the build below simply replaces the tag).
# ------------------------------------------------------------------------------
# Image Cache Check & Rebuild Prompt
# ------------------------------------------------------------------------------
if docker image inspect "$IMAGE_NAME" &>/dev/null 2>&1; then
    echo "ℹ️   Image '$IMAGE_NAME' already exists."
    read -r -p "    Rebuild? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping build. Using existing image."
        exit 0
    fi
    docker rmi "$IMAGE_NAME" || true
fi

# ------------------------------------------------------------------------------
# Docker Image Build Invocation
# ------------------------------------------------------------------------------
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
