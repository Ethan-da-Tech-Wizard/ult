#!/usr/bin/env python3

# ==============================================================================
# Program: check_requirements.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Pre-flight system requirements and readiness verification orchestrator for The Sacred Tech.
#          Performs tiered environment discovery validating Python 3.10+ runtimes, virtual environments,
#          package dependencies, Docker engine/daemon presence, and QEMU hardware emulation capabilities,
#          providing actionable installation recommendations across Windows, macOS, and Linux platforms.
# ==============================================================================

# How this file fits the app: read-only diagnostic (python setup/check_requirements.py). It changes nothing; it reports which of the three "tiers" are available so a player knows whether the game will use real Docker/QEMU or the built-in fallbacks.
# Tier 1 = Python 3.10+, the .venv and the packages (required). Tier 2 = Docker for the Arch sandbox (optional). Tier 3 = QEMU for the TempleOS VM (optional). The fix for anything missing is setup/install_all.py.
# Exit status is always 0: the result is only printed, so it cannot be used as a CI gate. The check imports the packages with the CURRENT interpreter, not the .venv one, so it can report "missing" when the packages are only installed in .venv; run it with .venv/bin/python for an accurate answer.
import os
import shutil
import subprocess
import sys

# ANSI colour codes; terminals that do not understand them (some Windows consoles) will show the raw escape text.
# ANSI escape sequence color palettes for terminal reporting
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def print_header(title):
    """Prints a styled section header banner."""
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")


# Prints one aligned result row; column widths (30 and 15) keep the table tidy for the longest labels used below.
def print_status(name, status, details="", is_ok=True):
    """Formats and prints an individual requirement verification row.

    Args:
        name: Name of the component or tool being checked.
        status: Short status label ('PASSED', 'FAILED', 'FOUND', etc.).
        details: Additional contextual information or version strings.
        is_ok: Boolean indicating passing status.
    """
    color = GREEN if is_ok else RED
    symbol = "✅" if is_ok else "❌"
    print(f" {symbol}  {BOLD}{name:<30}{RESET} : {color}{status:<15}{RESET} {details}")


# shutil.which searches PATH exactly as the shell would, so no subprocess is needed.
def check_command(cmd):
    """Queries system PATH to verify presence of an executable binary."""
    return shutil.which(cmd) is not None


def main():
    """Main verification pipeline executing tiered system capability checks."""
    print(f"\n{BOLD}{YELLOW}=========================================================={RESET}")
    print(f"{BOLD}{YELLOW}      The Sacred Tech — System Requirements Checker       {RESET}")
    print(f"{BOLD}{YELLOW}=========================================================={RESET}")

    # --------------------------------------------------------------------------
    # Tier 1: Core Python & Package Dependencies (Mandatory)
    # --------------------------------------------------------------------------
    print_header("Tier 1: Core JRPG Game (Required)")

    # The code base uses syntax and library features from Python 3.10 (and FastAPI/pydantic releases that require it).
    # 1. Python Version Check: Requires 3.10+
    major, minor = sys.version_info.major, sys.version_info.minor
    py_ok = major == 3 and minor >= 10
    py_ver_str = f"{major}.{minor}.{sys.version_info.micro}"
    if py_ok:
        print_status("Python 3.10+ Version", "PASSED", f"(Found {py_ver_str})", is_ok=True)
    else:
        print_status("Python 3.10+ Version", "FAILED", f"(Found {py_ver_str} - Upgrade to Python 3.10+)", is_ok=False)

    # .venv is the location install_all.py and scripts/run_dev.sh create; its absence only means the setup step has not been run.
    # 2. Virtual Environment check
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_dir = os.path.join(project_root, ".venv")
    venv_exists = os.path.exists(venv_dir)

    if venv_exists:
        print_status("Virtual Env (.venv)", "FOUND", f"({venv_dir})", is_ok=True)
    else:
        print_status("Virtual Env (.venv)", "MISSING", "(Run python setup/install_all.py)", is_ok=False)

    # `__import__` only tests that import works; versions are not checked.
    # 3. Python package imports check
    packages = ["fastapi", "uvicorn", "numpy", "pydantic"]
    missing_packages = []
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)

    if not missing_packages:
        print_status("Python Packages", "PASSED", "(fastapi, uvicorn, numpy, pydantic present)", is_ok=True)
    else:
        print_status("Python Packages", "INCOMPLETE", f"(Missing: {', '.join(missing_packages)})", is_ok=False)

    # --------------------------------------------------------------------------
    # Tier 2: Docker Engine & Container Sandbox (Optional)
    # --------------------------------------------------------------------------
    print_header("Tier 2: Arch Linux Sandbox (Optional)")

    # `docker info` succeeds only when the daemon is reachable (CLI present is not enough). Output is discarded; only the exit code matters.
    has_docker = check_command("docker")

    if has_docker:
        # Check if daemon is running and responsive
        daemon_ok = False
        try:
            res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            daemon_ok = res.returncode == 0
        except Exception:
            pass

        if daemon_ok:
            print_status("Docker CLI & Daemon", "PASSED", "(Ready to run compiler containers)", is_ok=True)
        else:
            print_status("Docker CLI & Daemon", "PARTIAL", "(Docker CLI installed, but daemon is NOT running)", is_ok=False)
            print(f"     {YELLOW}👉 Start Docker Desktop (or run 'sudo systemctl start docker'){RESET}")
    else:
        print_status("Docker Engine", "MISSING", "(Optional: required for Arch Linux Sandbox)", is_ok=False)
        print(f"     {YELLOW}👉 Download from: https://www.docker.com/products/docker-desktop/{RESET}")

    # --------------------------------------------------------------------------
    # Tier 3: QEMU Hypervisor & TempleOS VM (Optional)
    # --------------------------------------------------------------------------
    print_header("Tier 3: TempleOS VM Altar (Optional)")
    has_qemu = check_command("qemu-system-x86_64")

    if has_qemu:
        print_status("QEMU System Emulator", "PASSED", "(qemu-system-x86_64 found)", is_ok=True)
    else:
        print_status("QEMU System Emulator", "MISSING", "(Optional: required to run TempleOS VM)", is_ok=False)
        if sys.platform.startswith("win"):
            print(f"     {YELLOW}👉 Install: winget install SoftwareDesignLabs.QEMU{RESET}")
        elif sys.platform.startswith("darwin"):
            print(f"     {YELLOW}👉 Install: brew install qemu{RESET}")
        else:
            print(f"     {YELLOW}👉 Install: sudo apt install qemu-system-x86 qemu-utils{RESET}")

    # --------------------------------------------------------------------------
    # Readiness Summary Matrix & Actionable Guidance
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}{YELLOW}=========================================================={RESET}")
    print(f"{BOLD}{YELLOW}                  Readiness Summary                       {RESET}")
    print(f"{BOLD}{YELLOW}=========================================================={RESET}")

    # Tier 1 must pass entirely; tiers 2 and 3 only upgrade the experience (fallback modes exist in server/sandbox_manager.py and server/qemu_launcher.py).
    t1_ready = py_ok and venv_exists and not missing_packages
    t2_ready = has_docker
    t3_ready = has_qemu

    if t1_ready:
        print(f" 🟢  {BOLD}Tier 1 Core JRPG:{RESET}  {GREEN}READY TO PLAY!{RESET}")
    else:
        print(f" 🔴  {BOLD}Tier 1 Core JRPG:{RESET}  {RED}NOT READY (Please run setup first){RESET}")

    print(f" {'🟢' if t2_ready else '🟡'}  {BOLD}Tier 2 Sandbox:{RESET}    {'Active' if t2_ready else 'Fallback Mode (Host Execution)'}")
    print(f" {'🟢' if t3_ready else '🟡'}  {BOLD}Tier 3 VM:{RESET}         {'Active' if t3_ready else 'Fallback Mode (Simulated Altar)'}")

    print(f"\n{BOLD}{CYAN}Recommendations:{RESET}")
    if not t1_ready:
        print("  1. Run the auto-installer: python setup/install_all.py")
    else:
        print("  You are ready to launch! Run one of these commands to start the server:")
        if sys.platform.startswith("win"):
            print("  Windows powershell:  .\\scripts\\run_dev.ps1")
        else:
            print("  macOS/Linux bash:    ./scripts/run_dev.sh")

    print(f"{BOLD}{YELLOW}=========================================================={RESET}\n")


if __name__ == "__main__":
    main()
