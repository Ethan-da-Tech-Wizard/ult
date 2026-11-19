# ==============================================================================
# Program: build_desktop.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Desktop application packaging orchestrator compiling the Sacred Tech engine.
#          Assembles the FastAPI asynchronous backend, static web client HTML/JS/CSS assets,
#          and Docker sandbox test framework definitions into a standalone, single-file
#          executable using PyInstaller and UV. Configures cross-platform path separators,
#          manages bundle manifests, and relocates compiled binary artifacts into export storage.
# ==============================================================================

# How this file fits the app: developer tool (python server/build_desktop.py) that packages the app into one
# executable with PyInstaller (also run by .github/workflows/release.yml; Zeus_Assistant.spec is the
# PyInstaller spec file). Output ends up in save_data/export/.
# It bundles the client and sandbox folders as data; server/main.py and sandbox_manager.py find them through
# sys._MEIPASS at run time. Needs pyinstaller (or the `uv` tool, which provides it on the fly).
import os
import shutil
import subprocess
import sys


# Orchestrates the build; exits with status 1 on failure so CI notices.
def main():
    """Main desktop binary packaging pipeline."""
    print("====================================================")
    print("Building The Sacred Tech JRPG Desktop Assistant...")
    print("====================================================")

    # --------------------------------------------------------------------------
    # 1. Filesystem Paths & Export Directory Configuration
    # --------------------------------------------------------------------------
    # Derive canonical absolute directory paths independent of invoking working directory
    server_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(server_dir, ".."))
    export_dir = os.path.join(project_root, "save_data", "export")

    # Ensure export directory exists to receive compiled single-file binary
    os.makedirs(export_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # 2. Cross-Platform Asset Bundle Separator Resolution
    # --------------------------------------------------------------------------

    # `--add-data SRC<sep>DEST`: the separator differs by platform (";" on Windows, ":" elsewhere). DEST
    # ("client", "sandbox") becomes the folder name inside sys._MEIPASS.
    # PyInstaller requires semicolon (;) delimiter on Windows, colon (:) on POSIX systems
    sep = ";" if sys.platform.startswith("win") else ":"

    # Define asset directories to bundle into PyInstaller _MEIPASS runtime archive
    client_bundle = f"{os.path.join(project_root, 'client')}{sep}client"
    sandbox_bundle = f"{os.path.join(project_root, 'sandbox')}{sep}sandbox"

    # --------------------------------------------------------------------------
    # 3. PyInstaller Invocation Command Construction
    # --------------------------------------------------------------------------
    exe_name = "Zeus_Assistant"

    # Prefer the pyinstaller that sits next to the running Python (virtualenv case) so the build uses the same
    # environment; otherwise rely on PATH.
    # Attempt to locate pyinstaller in the same directory as the executing Python interpreter
    pyinstaller_bin = "pyinstaller"
    python_dir = os.path.dirname(sys.executable)
    candidate = os.path.join(python_dir, "pyinstaller" + (".exe" if sys.platform.startswith("win") else ""))
    if os.path.exists(candidate):
        pyinstaller_bin = candidate

    # --onefile packs everything into one self-extracting executable; --clean wipes PyInstaller's cache so
    # stale modules are not reused.
    pyinstaller_args = [
        pyinstaller_bin,
        "--onefile",
        f"--name={exe_name}",
        f"--add-data={client_bundle}",
        f"--add-data={sandbox_bundle}",
        "--clean",
        os.path.join(server_dir, "main.py"),
    ]

    print(f"Project root: {project_root}")
    print(f"Export directory: {export_dir}")
    print(f"Executing: {' '.join(pyinstaller_args)}")

    # --------------------------------------------------------------------------
    # 4. Packaging Subprocess Execution (UV vs Standard PyInstaller)
    # --------------------------------------------------------------------------

    # If `uv` is installed, run PyInstaller in a throw-away environment with the project's requirements;
    # otherwise use the current interpreter's PyInstaller.
    try:
        # Detect if UV package manager is available for fast ephemeral dependency resolution
        use_uv = False
        try:
            uv_check = subprocess.run(["uv", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if uv_check.returncode == 0:
                use_uv = True
        except FileNotFoundError:
            pass

        if use_uv:
            print("Invoking PyInstaller via UV ephemeral environment...")
            cmd = [
                "uv", "run",
                "--with", "pyinstaller",
                "--with-requirements", os.path.join(project_root, "requirements.txt"),
            ] + pyinstaller_args
            subprocess.run(cmd, check=True)
        else:
            print("UV not detected. Running standard PyInstaller in current interpreter environment...")
            subprocess.run(pyinstaller_args, check=True)

        # PyInstaller writes to <root>/dist; move the file to save_data/export (which is git-ignored) so it is
        # easy to find. A missing file only prints an error (no non-zero exit), which a CI step would not
        # detect.
        # --------------------------------------------------------------------------
        # 5. Build Artifact Relocation to Destination Export Store
        # --------------------------------------------------------------------------
        dist_dir = os.path.join(project_root, "dist")
        built_file = os.path.join(dist_dir, exe_name + (".exe" if sys.platform.startswith("win") else ""))
        target_file = os.path.join(export_dir, exe_name + (".exe" if sys.platform.startswith("win") else ""))

        if os.path.exists(built_file):
            shutil.move(built_file, target_file)
            print(f"\nSUCCESS! Desktop app packaged at: {target_file}")
        else:
            print(f"\nError: Built binary not found at expected location: {built_file}")

    except subprocess.CalledProcessError as e:
        print(f"\nError: Build command failed with exit code: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError occurred during package execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
