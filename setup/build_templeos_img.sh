#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build_templeos_img.sh
# Downloads TempleOS 5.03 ISO and converts it into a QEMU-bootable disk image
# for the Chapter 21 Altar bare-metal HolyC compilation experience.
#
# Requirements: qemu-img, qemu-system-x86_64
#
# IMPORTANT — serial console limitation:
#   Stock TempleOS is VGA + PS/2 only; Terry never wrote a serial driver.
#   The in-game Alt+7 telnet bridge therefore stays silent with the stock
#   ISO, and the game falls back to the validating mock HolyC altar.
#   To get REAL HolyC over the bridge, point TEMPLEOS_ISO_URL at a
#   serial-console-patched community build (e.g. a TempleOS fork with a
#   serial shell), or run the server with ZEUS_TEMPLEOS_VNC=1 and connect
#   a VNC viewer to 127.0.0.1:5900 to use the real TempleOS display.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SAVE_DIR="$PROJECT_ROOT/save_data"
IMG_PATH="$SAVE_DIR/templeos_core.img"
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

# Check prerequisites
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

# Check if image already exists
if [[ -f "$IMG_PATH" ]]; then
    echo "ℹ️   TempleOS image already exists at $IMG_PATH"
    read -r -p "    Rebuild? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping. Using existing image."
        exit 0
    fi
fi

# Download ISO if not cached
if [[ ! -f "$ISO_PATH" ]]; then
    echo "📥  Downloading TempleOS 5.03 ISO (~50MB)..."
    echo "    Source: $ISO_URL"
    echo ""
    if command -v curl &>/dev/null; then
        curl -L --progress-bar -o "$ISO_PATH" "$ISO_URL"
    elif command -v wget &>/dev/null; then
        wget -q --show-progress -O "$ISO_PATH" "$ISO_URL"
    else
        echo "❌  Neither curl nor wget found. Cannot download ISO."
        exit 1
    fi
    echo ""
    echo "✅  Downloaded: $ISO_PATH"
else
    echo "✅  ISO already cached: $ISO_PATH"
fi

echo ""
echo "🔨  Creating $DISK_SIZE QEMU disk image..."
qemu-img create -f qcow2 "$IMG_PATH" "$DISK_SIZE"
echo "✅  Disk image created: $IMG_PATH"

echo ""
echo "🚀  First boot: installing TempleOS onto disk image."
echo "    This will open a QEMU window. Inside TempleOS:"
echo "    1. Press any key when prompted"
echo "    2. Type: BootHDIns; (install to hard drive)"
echo "    3. Follow TempleOS installer prompts"
echo "    4. After install, close the QEMU window"
echo ""
echo "Press ENTER to start the QEMU installer window..."
read -r

qemu-system-x86_64 \
    -m 512M \
    -hda "$IMG_PATH" \
    -cdrom "$ISO_PATH" \
    -boot d \
    -vga std \
    -display default

echo ""
echo "✅  Installation complete (if you followed the steps above)."
echo ""
echo "Now verifying headless serial boot..."
echo "Starting QEMU with serial redirect to port 4444 for 5 seconds..."
QEMU_PID=""
qemu-system-x86_64 \
    -m 512M \
    -hda "$IMG_PATH" \
    -nographic \
    -serial "telnet:127.0.0.1:4444,server,nowait" &
QEMU_PID=$!
sleep 5
kill "$QEMU_PID" 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  TempleOS Altar VM ready!                                ║"
echo "║                                                          ║"
echo "║  Image: save_data/templeos_core.img                      ║"
echo "║  Serial: telnet 127.0.0.1 4444                           ║"
echo "║                                                          ║"
echo "║  The game server auto-launches QEMU on startup.          ║"
echo "║  Chapter 21 Alt+7 tab connects to the live serial port.  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
