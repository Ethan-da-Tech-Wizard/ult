import os
import sys
import subprocess
import logging

logger = logging.getLogger("ZeusSandbox")

SANDBOX_CONTAINER_NAME = "zeus-sandbox"

# Resolve directories dynamically (supports PyInstaller bundle assets)
if hasattr(sys, '_MEIPASS'):
    WORKSPACE_DIR = os.getcwd()
    BUNDLED_SANDBOX_DIR = os.path.join(sys._MEIPASS, "sandbox")
else:
    WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    BUNDLED_SANDBOX_DIR = os.path.join(WORKSPACE_DIR, "sandbox")

RELIC_SAVE_DIR = os.path.join(WORKSPACE_DIR, "save_data", "relic_save")

def ensure_sandbox_running():
    """Checks if the Docker sandbox is running. If not, attempts to start it."""
    try:
        # Check if container is running
        check_run = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", SANDBOX_CONTAINER_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if check_run.returncode == 0 and check_run.stdout.strip() == "true":
            return True
            
        # Check if container exists but is stopped
        check_exist = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={SANDBOX_CONTAINER_NAME}", "-q"],
            stdout=subprocess.PIPE,
            text=True
        )
        if check_exist.stdout.strip():
            logger.info("Starting stopped sandbox container...")
            start_proc = subprocess.run(["docker", "start", SANDBOX_CONTAINER_NAME])
            return start_proc.returncode == 0
            
        # Container does not exist, run a new instance
        # Mount relic_save to /workspace inside container
        logger.info("Launching new sandbox container...")
        run_cmd = [
            "docker", "run", "-d",
            "--name", SANDBOX_CONTAINER_NAME,
            "-v", f"{RELIC_SAVE_DIR}:/workspace",
            "-v", f"{BUNDLED_SANDBOX_DIR}:/sandbox",
            "-w", "/workspace",
            "zeus-arch:latest",
            "tail", "-f", "/dev/null"
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
    """Executes the test suite inside the running sandbox container for a given chapter."""
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
                timeout=15
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout + res.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Execution timed out (15s limit). Infinite loop detected?"}
        except Exception as e:
            return {"success": False, "output": f"Local execution failed: {e}"}

    # Run test inside container
    test_script = f"/sandbox/test_frameworks/ch{chapter_id}_test.py"
    exec_cmd = ["docker", "exec", SANDBOX_CONTAINER_NAME, "python", test_script]
    try:
        res = subprocess.run(
            exec_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
        return {
            "success": res.returncode == 0,
            "output": res.stdout + res.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Execution timed out inside container (15s limit)."}
    except Exception as e:
        return {"success": False, "output": f"Docker exec failed: {e}"}
