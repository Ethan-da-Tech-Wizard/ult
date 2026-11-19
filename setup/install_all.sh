#!/usr/bin/env bash

# ==============================================================================
# Program: install_all.sh
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: POSIX shell wrapper script delegating to the unified Python setup installer.
#          Verifies host Python 3.10+ interpreter presence and passes command line arguments
#          directly to setup/install_all.py for virtual environment, container, and VM provisioning.
# ==============================================================================

# Halt on error (-e), treat uninitialized variables as fatal errors (-u),
# and prevent pipe masking of intermediate non-zero return codes (-o pipefail).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verify python3 interpreter presence on system PATH
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Please install Python 3.10+ first."
    exit 1
fi

# Execute Python installer with passed CLI arguments
exec python3 "$SCRIPT_DIR/install_all.py" "$@"
