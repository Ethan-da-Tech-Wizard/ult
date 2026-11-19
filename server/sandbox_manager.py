# ==============================================================================
# Program: sandbox_manager.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Docker container runtime manager executing algorithmic solution submissions in isolated secure sandboxes.
#          Inspects daemon health, provisions ephemeral container instances with bind mounts,
#          enforces 15-second execution timeouts against algorithmic denial-of-service,
#          and implements fallback local subprocess execution when container virtualization is unavailable.
# ==============================================================================

import logging
import os
import subprocess
import sys

logger = logging.getLogger("ZeusSandbox")

# Constant identifier for the isolated Docker container runtime
SANDBOX_CONTAINER_NAME = "zeus-sandbox"

# ------------------------------------------------------------------------------
# Directory Resolution Architecture (Handles PyInstaller _MEIPASS Bundle Extraction)
# ------------------------------------------------------------------------------
# When bundled into a standalone executable via PyInstaller, sys._MEIPASS holds the
# path to the temporary directory where bundled files are extracted at launch.
if hasattr(sys, "_MEIPASS"):
    WORKSPACE_DIR = os.getcwd()
    BUNDLED_SANDBOX_DIR = os.path.join(sys._MEIPASS, "sandbox")
else:
    WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    BUNDLED_SANDBOX_DIR = os.path.join(WORKSPACE_DIR, "sandbox")

# Persistent directory storing user solution files accessible inside container volume
RELIC_SAVE_DIR = os.path.join(WORKSPACE_DIR, "save_data", "relic_save")


def ensure_sandbox_running():
    """Verifies that the Docker sandbox container is active, starting or creating it if necessary.

    Container Lifecycle Invariants:
      1. Inspection: Queries Docker daemon for existing container running status.
      2. Restart: If container exists but is stopped, restarts it without recreating volumes.
      3. Provisioning: If container does not exist, launches a fresh daemonized container
         mounting user code (`/workspace`) and validator scripts (`/sandbox`) in read/write mode.

    Returns:
        bool: True if container is active and reachable; False on Docker daemon failure.
    """
    try:
        # Step 1: Query Docker daemon to verify container existence and running state via inspect format string
        check_run = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", SANDBOX_CONTAINER_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if check_run.returncode == 0 and check_run.stdout.strip() == "true":
            return True

        # Step 2: Check if container exists in stopped state to avoid recreating container volumes
        check_exist = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={SANDBOX_CONTAINER_NAME}", "-q"],
            stdout=subprocess.PIPE,
            text=True,
        )
        if check_exist.stdout.strip():
            logger.info("Starting stopped sandbox container...")
            start_proc = subprocess.run(["docker", "start", SANDBOX_CONTAINER_NAME])
            return start_proc.returncode == 0

        # Step 3: Container does not exist, provision isolated instance with bind mounted save volume
        logger.info("Launching new sandbox container...")
        run_cmd = [
            "docker", "run", "-d",
            "--name", SANDBOX_CONTAINER_NAME,
            "-v", f"{RELIC_SAVE_DIR}:/workspace",
            "-v", f"{BUNDLED_SANDBOX_DIR}:/sandbox",
            "-w", "/workspace",
            "zeus-arch:latest",
            "tail", "-f", "/dev/null",
        ]
        run_proc = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if run_proc.returncode != 0:
            logger.error(f"Failed to launch container: {run_proc.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking/starting sandbox: {e}")
        return False


def execute_test(chapter_id: int):
    """Executes the test suite for a given chapter inside the running sandbox or local fallback.

    Execution Pipeline & Concurrency Bounds:
      - Validates Docker container presence via `ensure_sandbox_running()`.
      - If Docker daemon is unavailable, falls back to executing tests locally with `sys.executable`.
      - Enforces a strict 15-second timeout window preventing infinite loops or CPU exhaustion.
      - Aggregates combined stdout and stderr streams for display in the client UI.

    Args:
        chapter_id: Numerical chapter index identifying the test framework (0-21).

    Returns:
        dict: Mapping containing boolean 'success' flag and string 'output' buffer.
    """
    if not ensure_sandbox_running():
        # Fallback to local execution if Docker is not installed or running
        logger.warning("Docker sandbox not running. Executing tests locally as fallback.")
        local_test_path = os.path.join(BUNDLED_SANDBOX_DIR, "test_frameworks", f"ch{chapter_id}_test.py")
        if not os.path.exists(local_test_path):
            return {"success": False, "output": f"Test suite ch{chapter_id}_test.py not found."}
        try:
            res = subprocess.run(
                [sys.executable, local_test_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout + res.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Execution timed out (15s limit). Infinite loop detected?"}
        except Exception as e:
            return {"success": False, "output": f"Local execution failed: {e}"}

    # Execute test script inside the isolated Docker container
    test_script = f"/sandbox/test_frameworks/ch{chapter_id}_test.py"
    exec_cmd = ["docker", "exec", SANDBOX_CONTAINER_NAME, "python", test_script]
    try:
        res = subprocess.run(
            exec_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
        return {
            "success": res.returncode == 0,
            "output": res.stdout + res.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Execution timed out inside container (15s limit)."}
    except Exception as e:
        return {"success": False, "output": f"Docker exec failed: {e}"}
