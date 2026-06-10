#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# install_all.py — The Sacred Tech unified cross-platform setup installer
#
# Sets up everything needed to play:
#   Tier 1 (required): Python venv + packages from requirements.txt
#   Tier 2 (optional): Arch Linux compiler sandbox container (via Docker)
#   Tier 3 (optional): TempleOS Altar VM image (via QEMU)
#
# Usage:
#   python setup/install_all.py           (interactive prompt)
#   python setup/install_all.py --minimal (Tier 1 only, no prompts)
#   python setup/install_all.py --full    (All tiers supported, no prompts)
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import subprocess
import shutil
import argparse

def ask_yes_no(question, default="y", mode="interactive"):
    if mode == "minimal":
        return False
    if mode == "full":
        return True
    
    prompt = " [Y/n] " if default == "y" else " [y/N] "
    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if not resp:
                return default == "y"
            if resp in ("y", "yes"):
                return True
            if resp in ("n", "no"):
                return False
        except (KeyboardInterrupt, EOFError):
            print()
            return False

def check_command(cmd):
    return shutil.which(cmd) is not None

def main():
    parser = argparse.ArgumentParser(description="The Sacred Tech Setup Tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--minimal", action="store_true", help="Tier 1 only, no prompts")
    group.add_argument("--full", action="store_true", help="All tiers the machine supports, no prompts")
    args = parser.parse_args()

    mode = "interactive"
    if args.minimal:
        mode = "minimal"
    elif args.full:
        mode = "full"

    print("\n==========================================================")
    print("   The Sacred Tech — Unified Setup Installer              ")
    print("==========================================================\n")

    # 1. Verify Python version
    major, minor = sys.version_info.major, sys.version_info.minor
    print(f"✅  Python {major}.{minor} detected.")
    if major < 3 or (major == 3 and minor < 10):
        print(f"❌  Python 3.10+ is required (found {major}.{minor}).")
        sys.exit(1)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_dir = os.path.join(project_root, ".venv")
    requirements_path = os.path.join(project_root, "requirements.txt")

    tier1_status = "not installed"
    tier2_status = "skipped"
    tier3_status = "skipped"

    # -- Tier 1: Core Setup --
    print("\n── Tier 1: Core game (Python dependencies) ──")
    if not os.path.exists(venv_dir):
        print("📦  Creating virtual environment at .venv ...")
        # Use sys.executable to ensure we spawn using the running python binary
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    # Resolve venv python binary path based on OS
    if sys.platform.startswith("win"):
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(venv_python):
        print(f"❌  Failed to locate virtual environment Python binary at {venv_python}")
        sys.exit(1)

    print("📦  Upgrading pip and installing requirements.txt ...")
    subprocess.run([venv_python, "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=True)
    subprocess.run([venv_python, "-m", "pip", "install", "--quiet", "-r", requirements_path], check=True)
    print("✅  Core game dependencies installed successfully.")
    tier1_status = f"installed (.venv at {venv_dir})"

    # -- Tier 2: Arch Linux Sandbox (Docker) --
    print("\n── Tier 2: Arch Linux sandbox (Docker) ──")
    docker_bin = "docker"
    has_docker = check_command(docker_bin)

    if not has_docker:
        print("ℹ️   Docker command not found — skipping.")
        print("    The in-game terminal will fall back to your host shell, and validators")
        print("    will run locally. Install Docker Desktop to run a real Arch sandbox.")
        tier2_status = "skipped (Docker not installed)"
    else:
        # Check if Docker daemon is reachable
        daemon_running = False
        try:
            res = subprocess.run([docker_bin, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            daemon_running = res.returncode == 0
        except Exception:
            pass

        if not daemon_running:
            print("ℹ️   Docker daemon is unreachable — skipping.")
            print("    This can happen if:")
            print("    1. The Docker service is not running. (Start Docker Desktop)")
            if sys.platform != "win32":
                print("    2. Permission is denied. (Add yourself to the docker group:)")
                print("       sudo usermod -aG docker $USER (then log out and log back in)")
            tier2_status = "skipped (Docker daemon unreachable)"
        elif ask_yes_no("Build the Arch Linux sandbox image (~1 GB download)?", mode=mode):
            image_exists = False
            try:
                res = subprocess.run([docker_bin, "image", "inspect", "zeus-arch:latest"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                image_exists = res.returncode == 0
            except Exception:
                pass

            if image_exists:
                print("✅  Image zeus-arch:latest already exists.")
            else:
                print("🏗️   Building zeus-arch:latest (this downloads Arch packages) ...")
                dockerfile_path = os.path.join(project_root, "sandbox", "Dockerfile")
                sandbox_path = os.path.join(project_root, "sandbox")
                subprocess.run([docker_bin, "build", "--tag", "zeus-arch:latest", "--file", dockerfile_path, sandbox_path], check=True)

            relic_save_dir = os.path.join(project_root, "save_data", "relic_save")
            os.makedirs(relic_save_dir, exist_ok=True)

            # Check container status
            container_running = False
            container_exists = False
            try:
                res_running = subprocess.run([docker_bin, "ps", "--filter", "name=zeus-sandbox", "-q"], stdout=subprocess.PIPE, text=True)
                container_running = bool(res_running.stdout.strip())
                if not container_running:
                    res_exists = subprocess.run([docker_bin, "ps", "-a", "--filter", "name=zeus-sandbox", "-q"], stdout=subprocess.PIPE, text=True)
                    container_exists = bool(res_exists.stdout.strip())
            except Exception:
                pass

            if container_running:
                print("✅  Container zeus-sandbox is already running.")
            elif container_exists:
                print("▶️   Starting existing zeus-sandbox container ...")
                subprocess.run([docker_bin, "start", "zeus-sandbox"], check=True)
            else:
                print("▶️   Launching new zeus-sandbox container ...")
                run_cmd = [
                    docker_bin, "run", "-d", "--name", "zeus-sandbox",
                    "-v", f"{relic_save_dir}:/workspace",
                    "-v", f"{os.path.join(project_root, 'sandbox')}:/sandbox",
                    "-w", "/workspace",
                    "zeus-arch:latest",
                    "tail", "-f", "/dev/null"
                ]
                subprocess.run(run_cmd, check=True)
            print("✅  Arch Linux sandbox ready.")
            tier2_status = "installed and running"
        else:
            tier2_status = "skipped (declined)"

    # -- Tier 3: TempleOS Altar VM (QEMU) --
    print("\n── Tier 3: TempleOS Altar VM (QEMU) ──")
    has_qemu = check_command("qemu-system-x86_64")
    image_path = os.path.join(project_root, "save_data", "templeos_core.img")

    if not has_qemu:
        print("ℹ️   QEMU not found — skipping.")
        print("    Chapter 21 will fall back to the built-in validating HolyC altar.")
        if sys.platform.startswith("win"):
            print("    To run the real VM, install QEMU via: winget install SoftwareDesignLabs.QEMU")
        else:
            print("    To run the real VM, install QEMU via homebrew or apt-get.")
        tier3_status = "skipped (QEMU not installed)"
    elif os.path.exists(image_path):
        print("✅  TempleOS core VM image already exists.")
        tier3_status = "already built"
    else:
        print("ℹ️   TempleOS image save_data/templeos_core.img not found.")
        print("    Building the VM image requires a terminal interaction.")
        if sys.platform.startswith("win"):
            print("    You can run setup/build_templeos_img.sh in a bash emulator (e.g. Git Bash) later.")
        else:
            if ask_yes_no("Build the TempleOS VM image now? (downloads the ISO and starts installer)", default="n", mode=mode):
                build_script = os.path.join(project_root, "setup", "build_templeos_img.sh")
                subprocess.run([build_script], check=True)
                tier3_status = "installed"
            else:
                tier3_status = "skipped (declined)"

    # -- Summary --
    print("\n==========================================================")
    print("   Setup Summary                                          ")
    print("==========================================================")
    print(f"  Tier 1 — Core JRPG game:   {tier1_status}")
    print(f"  Tier 2 — Arch sandbox:     {tier2_status}")
    print(f"  Tier 3 — TempleOS VM:      {tier3_status}")
    print("\n▶️   Play now:")
    if sys.platform.startswith("win"):
        print("      .\\scripts\\run_dev.ps1")
    else:
        print("      ./scripts/run_dev.sh")
    print("      Then open http://127.0.0.1:8000 in your browser.\n")

if __name__ == "__main__":
    main()
