# The Sacred Tech: Chronicles of the Source Code

A retro FF1-style educational JRPG where you write real code — command line,
SQL, attention layers, LoRA, Kubernetes, and bare-metal HolyC — to open
gates, defeat gatekeepers, and reach the Altar of TempleOS.

This document covers **everything you need to download and play**.

---

## TL;DR — Download and Play

```bash
git clone https://github.com/Ethan-da-Tech-Wizard/ult.git
cd ult
./setup/install_all.sh     # one file installs everything it can find
./scripts/run_dev.sh       # starts the game
```

Then open **http://127.0.0.1:8000** in your browser.

Don't want to run the installer? `./scripts/run_dev.sh` alone also works —
it bootstraps its own Python dependencies into a local `.venv` on first
launch, so by the time the game starts, everything it needs is on your
machine.

---

## Requirements

The game runs in three tiers. Only Tier 1 is required — the game detects
what you have and falls back gracefully for the rest.

| Tier | What it unlocks | What you need |
|------|----------------|----------------|
| **1. Core game (required)** | All 22 chapters, maps, combat, editor, validators, saves | **Python 3.10+** with `pip`. A modern browser. That's it. |
| **2. Arch Linux sandbox (optional)** | The Alt+5 terminal becomes a *real* Arch Linux container; chapter validators run sandboxed instead of on your host | **Docker** (Docker Desktop on macOS/Windows, `docker` on Linux) |
| **3. TempleOS Altar VM (optional)** | Chapter 21's Alt+7 tab drives a real TempleOS virtual machine | **QEMU** (`brew install qemu` / `sudo apt install qemu-system-x86 qemu-utils`) |

Without Tier 2 the terminal uses your host shell (a yellow badge in-game
tells you which one you're in). Without Tier 3 the Altar uses the built-in
validating HolyC console — same puzzles, no VM.

**Python packages** (installed automatically by the installer or first
launch): `fastapi`, `uvicorn[standard]`, `pydantic`, `numpy` — see
`requirements.txt`.

**Ports used** (all loopback-only, nothing is exposed to your network):
`8000` game server, `4444` TempleOS serial bridge, `5900` optional TempleOS
VNC display.

---

## The One-File Installer: `setup/install_all.sh`

Every download the game needs, handled by one script:

```bash
./setup/install_all.sh            # interactive: asks before optional tiers
./setup/install_all.sh --minimal  # Tier 1 only, no questions
./setup/install_all.sh --full     # everything your machine supports, no questions
```

What it does, in order:

1. Verifies Python 3.10+, creates a local `.venv`, installs all Python
   packages from `requirements.txt`.
2. If Docker is available: builds the `zeus-arch` sandbox image and starts
   the `zeus-sandbox` container (skipped silently if Docker is absent).
3. If QEMU is available: offers to build the TempleOS Altar VM image
   (requires a one-time interactive TempleOS install — see
   `setup/build_templeos_img.sh`).
4. Prints a summary of which tiers are active and how to launch.

Re-running it is safe — every step checks what already exists.

---

## Playing the Game

```bash
./scripts/run_dev.sh
```

Open **http://127.0.0.1:8000**. The game starts in darkness — that's the
tutorial. Follow the objective tracker.

**Controls**

| Key | Action |
|-----|--------|
| WASD / Arrows (hold to walk) | Move |
| Enter / Space / E | Talk, interact, advance dialogue |
| I | Inventory |
| Escape | Settings (palette, dialogue speed, audio, load earlier saves) |
| Tab (or Ctrl+E) | Toggle between exploring and the code editor |
| Alt+1…9 | Workspace tabs: Editor, Console, Chronicles, Codex, Terminal, Browser, TempleOS, Diagnostics, Library |
| Ctrl+Enter (in editor) | Compile & Run |

---

## Single-File Distribution (zero installs for players)

To hand someone the game as **one double-clickable file** with Python and
all packages baked in:

```bash
pip install pyinstaller
python server/build_desktop.py
```

This produces a standalone `Zeus_Assistant` executable (in
`save_data/export/`) bundling the server, client, and validators. The
recipient needs no Python, no pip, nothing — Tiers 2 and 3 remain optional
extras on their machine. Build it on the OS you're targeting (PyInstaller
doesn't cross-compile).

---

## Windows Notes

The setup scripts are bash — use **Git Bash** or **WSL**, or do Tier 1
manually:

```powershell
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python server\main.py
```

Then open http://127.0.0.1:8000.

---

## Troubleshooting

- **"Backend offline" in-game** — the server isn't running; start
  `./scripts/run_dev.sh` and refresh.
- **Terminal badge says "host shell fallback"** — Docker isn't running or
  the sandbox was never built. Run `./setup/install_all.sh --full` (or
  `setup/build_sandbox.sh`) with Docker started.
- **Chapter validators fail with `ModuleNotFoundError: numpy`** — your
  Python env predates the installer; re-run `./setup/install_all.sh`.
- **TempleOS tab shows the mock altar** — that's expected without the VM
  image. Note: the *stock* TempleOS ISO has no serial console, so the
  serial bridge only carries data with a serial-patched community build
  (`TEMPLEOS_ISO_URL=... setup/build_templeos_img.sh`). To see the real
  TempleOS display instead, launch with `ZEUS_TEMPLEOS_VNC=1` and connect a
  VNC viewer to `127.0.0.1:5900`.
- **Reset all progress** — delete `save_data/save_state.db` and
  `save_data/relic_save/`.
