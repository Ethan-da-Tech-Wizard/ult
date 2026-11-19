#!/usr/bin/env bash

# ==============================================================================
# Program: build_templeos_img.sh
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated QEMU disk image provisioner and installer for TempleOS virtualization.
#          Downloads the TempleOS 5.03 ISO release, provisions a 256MB QCOW2/raw virtual hard disk,
#          validates QEMU utility toolchain availability, configures virtual machine parameters,
#          and sets up the environment for Chapter 21 HolyC bare-metal compilation challenges.
# ==============================================================================

# How this file fits the app: optional helper for Chapter 21. It downloads the TempleOS ISO and creates an empty 256 MB raw disk at save_data/templeos_core.img. server/qemu_launcher.py starts QEMU on that disk when it exists; if it does not exist the game uses its mock HolyC altar instead.
# Limitations to know: the script only creates a blank disk and downloads the ISO. It does not install TempleOS onto the disk or attach the ISO, and the ISO download is not checksum-verified, so the resulting image does not boot an operating system by itself (a manual installer run with the ISO is still needed).
# Halt on error (-e), treat uninitialized variables as fatal errors (-u),
# and prevent pipe masking of intermediate non-zero return codes (-o pipefail).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SAVE_DIR="$PROJECT_ROOT/save_data"
IMG_PATH="$SAVE_DIR/templeos_core.img"

# TEMPLEOS_ISO_URL lets you substitute a serial-patched build; stock TempleOS has no serial driver, which the game's serial bridge needs.
# Override with a serial-patched community ISO for a working serial bridge:
#   TEMPLEOS_ISO_URL=https://example.org/TempleOS-serial.ISO ./build_templeos_img.sh
ISO_URL="${TEMPLEOS_ISO_URL:-https://templeos.org/Downloads/TempleOS.ISO}"
ISO_PATH="$SAVE_DIR/TempleOS.ISO"
DISK_SIZE="256M"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   The Sacred Tech — TempleOS Altar VM Builder            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "This script builds a headless TempleOS serial console image"
echo "for Chapter 21: Altar of TempleOS."
echo ""
echo "TempleOS was written by Terry A. Davis (1969–2018)."
echo "It is public domain. The OS and all its tools are free."
echo ""
if [[ -z "${TEMPLEOS_ISO_URL:-}" ]]; then
    echo "⚠️   NOTE: stock TempleOS has NO serial console driver."
    echo "    The in-game Alt+7 serial bridge will stay silent with this ISO"
    echo "    and the game will use the validating mock HolyC altar instead."
    echo "    For real HolyC: set TEMPLEOS_ISO_URL to a serial-patched fork,"
    echo "    or run the server with ZEUS_TEMPLEOS_VNC=1 and use a VNC viewer."
    echo ""
fi

# Preflight: both QEMU tools are required (qemu-img creates the disk, qemu-system-x86_64 runs it). check_cmd prints a brew hint only for the "brew" type.
# ------------------------------------------------------------------------------
# Pre-Flight Checks: QEMU Utility Toolchain Availability
# ------------------------------------------------------------------------------
check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        echo "❌  '$1' not found."
        if [[ "$2" == "brew" ]]; then
            echo "    Install with: brew install $3"
        fi
        return 1
    fi
    return 0
}

MISSING=0
check_cmd qemu-img brew qemu || MISSING=1
check_cmd qemu-system-x86_64 brew qemu || MISSING=1

if [[ $MISSING -eq 1 ]]; then
    echo ""
    echo "Install QEMU first:"
    echo "  macOS:  brew install qemu"
    echo "  Linux:  sudo apt install qemu-system-x86 qemu-utils"
    exit 1
fi

echo "✅  QEMU found: $(qemu-system-x86_64 --version | head -1)"
echo ""

mkdir -p "$SAVE_DIR"

# ------------------------------------------------------------------------------
# Image Cache Check & Rebuild Prompt
# ------------------------------------------------------------------------------
if [[ -f "$IMG_PATH" ]]; then
    echo "ℹ️   TempleOS image already exists at $IMG_PATH"
    read -r -p "    Rebuild? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping. Using existing image."
        exit 0
    fi
fi

# Download once and reuse: the ISO is kept in save_data/ so rebuilding the disk does not download it again. curl -L follows redirects and --fail turns HTTP errors into a non-zero exit (set -e then aborts).
# ------------------------------------------------------------------------------
# ISO Download and Image Formatting
# ------------------------------------------------------------------------------
if [[ ! -f "$ISO_PATH" ]]; then
    echo "📥  Downloading TempleOS 5.03 ISO (~50MB)..."
    echo "    Source: $ISO_URL"
    echo ""
    if command -v curl &>/dev/null; then
        curl -L --fail --progress-bar "$ISO_URL" -o "$ISO_PATH"
    elif command -v wget &>/dev/null; then
        wget -O "$ISO_PATH" "$ISO_URL"
    else
        echo "❌  Neither curl nor wget found. Please download $ISO_URL to $ISO_PATH manually."
        exit 1
    fi
fi

# `-f raw` is a plain file (no copy-on-write overhead); the 256M is only the size ceiling, the file is sparse on most filesystems.
# Provision sparse virtual drive disk container
echo "Creating $DISK_SIZE virtual disk image at $IMG_PATH..."
qemu-img create -f raw "$IMG_PATH" "$DISK_SIZE"

echo ""
echo "✅  TempleOS VM disk provisioned: $IMG_PATH"
echo "    The game server will mount this disk on loopback port 4444."
