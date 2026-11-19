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

import os
import shutil
import subprocess
import sys


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
    # PyInstaller requires semicolon (;) delimiter on Windows, colon (:) on POSIX systems
    sep = ";" if sys.platform.startswith("win") else ":"

    # Define asset directories to bundle into PyInstaller _MEIPASS runtime archive
    client_bundle = f"{os.path.join(project_root, 'client')}{sep}client"
    sandbox_bundle = f"{os.path.join(project_root, 'sandbox')}{sep}sandbox"

    # --------------------------------------------------------------------------
    # 3. PyInstaller Invocation Command Construction
    # --------------------------------------------------------------------------
    exe_name = "Zeus_Assistant"

    # Attempt to locate pyinstaller in the same directory as the executing Python interpreter
    pyinstaller_bin = "pyinstaller"
    python_dir = os.path.dirname(sys.executable)
    candidate = os.path.join(python_dir, "pyinstaller" + (".exe" if sys.platform.startswith("win") else ""))
    if os.path.exists(candidate):
        pyinstaller_bin = candidate

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
