#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# check_requirements.py — System Requirements Checker for The Sacred Tech
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import shutil
import subprocess

# Terminal colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

def print_header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")

def print_status(name, status, details="", is_ok=True):
    color = GREEN if is_ok else RED
    symbol = "✅" if is_ok else "❌"
    print(f" {symbol}  {BOLD}{name:<30}{RESET} : {color}{status:<15}{RESET} {details}")

def check_command(cmd):
    return shutil.which(cmd) is not None

def main():
    print(f"\n{BOLD}{YELLOW}=========================================================={RESET}")
    print(f"{BOLD}{YELLOW}      The Sacred Tech — System Requirements Checker       {RESET}")
    print(f"{BOLD}{YELLOW}=========================================================={RESET}")

    # ── TIER 1: Python & PIP dependencies ──
    print_header("Tier 1: Core JRPG Game (Required)")
    
    # Python Version Check
    major, minor = sys.version_info.major, sys.version_info.minor
    py_ok = major == 3 and minor >= 10
    py_ver_str = f"{major}.{minor}.{sys.version_info.micro}"
    if py_ok:
        print_status("Python 3.10+ Version", "PASSED", f"(Found {py_ver_str})", is_ok=True)
    else:
        print_status("Python 3.10+ Version", "FAILED", f"(Found {py_ver_str} - Upgrade to Python 3.10+)", is_ok=False)

    # Virtual Environment check
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_dir = os.path.join(project_root, ".venv")
    venv_exists = os.path.exists(venv_dir)
    
    if venv_exists:
        print_status("Virtual Env (.venv)", "FOUND", f"({venv_dir})", is_ok=True)
    else:
        print_status("Virtual Env (.venv)", "MISSING", f"(Run python setup/install_all.py)", is_ok=False)

    # Python packages check
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

    # ── TIER 2: Docker / Sandbox ──
    print_header("Tier 2: Arch Linux Sandbox (Optional)")
    has_docker = check_command("docker")
    
    if has_docker:
        # Check if daemon is running
        daemon_ok = False
        try:
            res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            daemon_ok = res.returncode == 0
        except Exception:
            pass
            
        if daemon_ok:
            print_status("Docker CLI & Daemon", "PASSED", "(Ready to run compiler containers)", is_ok=True)
        else:
            print_status("Docker CLI & Daemon", "PARTIAL", f"(Docker CLI installed, but daemon is NOT running)", is_ok=False)
            print(f"     {YELLOW}👉 Start Docker Desktop (or run 'sudo systemctl start docker'){RESET}")
    else:
        print_status("Docker Engine", "MISSING", "(Optional: required for Arch Linux Sandbox)", is_ok=False)
        print(f"     {YELLOW}👉 Download from: https://www.docker.com/products/docker-desktop/{RESET}")

    # ── TIER 3: QEMU / TempleOS VM ──
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

    # ── SUMMARY ──
    print(f"\n{BOLD}{YELLOW}=========================================================={RESET}")
    print(f"{BOLD}{YELLOW}                  Readiness Summary                       {RESET}")
    print(f"{BOLD}{YELLOW}=========================================================={RESET}")
    
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
