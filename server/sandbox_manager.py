# ==============================================================================
# Program: sandbox_manager.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Docker container runtime manager executing algorithmic solution submissions in isolated secure sandboxes.
#          Inspects daemon health, provisions ephemeral container instances with bind mounts,
#          enforces 15-second execution timeouts against algorithmic denial-of-service,
#          and implements fallback local subprocess execution when container virtualization is unavailable.
# ==============================================================================

# How this file fits the app: called by server/main.py (POST /api/compile -> execute_test, GET
# /api/diagnostics -> paths). It runs the per-chapter validator scripts in sandbox/test_frameworks/ against
# the player's saved solution.
# Modes: (1) DEFAULT: each grading run is a fresh, locked-down `docker run --rm` of the "zeus-arch" image
# (no network, memory/CPU/pids limits, read-only root, non-root user, all capabilities dropped, validators and
# player files mounted read-only) with a real timeout that `docker kill`s the container by name.
# (2) When Docker is missing, player code is NOT run. execute_test raises SandboxUnavailable (the route
# answers 503) unless the operator sets ULT_ALLOW_HOST_EXEC=1, which runs the validator with the host's
# Python as the current user. That is UNSAFE and logs a loud warning on every run.
# The long-lived `zeus-sandbox` container is only used by the Alt+5 terminal (hardened with the same flags).
# Test: tests/test_compile_no_host_exec.py, tests/test_sandbox_argv.py (no Docker needed).
import logging
import os
import secrets
import shutil
import subprocess
import sys

# Logger name shown in server output.
logger = logging.getLogger("ZeusSandbox")

# Name used for `docker inspect/exec/start`; also checked by server/main.py (sandbox status and the shell
# bridge), so change it everywhere or nowhere.
# Constant identifier for the isolated Docker container runtime
SANDBOX_CONTAINER_NAME = "zeus-sandbox"

# Image built by setup/build_sandbox.sh. (Still the unpinned rolling Arch base; pinning by digest is future work.)
SANDBOX_IMAGE = "zeus-arch:latest"
# Resource limits for every grading container. Generous for numpy/sqlite chapters, small for a fork bomb.
RUN_MEMORY = "512m"
RUN_CPUS = "1"
RUN_PIDS_LIMIT = "128"
# Unprivileged uid:gid ("nobody") inside the container.
RUN_USER = "65534:65534"
# Wall-clock limit for one grading run, enforced by killing the container (not just the docker CLI).
RUN_TIMEOUT_SECONDS = 15

HOST_EXEC_ENV = "ULT_ALLOW_HOST_EXEC"


class SandboxUnavailable(RuntimeError):
    """No safe place to run player code (Docker missing) and host execution was not explicitly enabled."""


UNAVAILABLE_MESSAGE = (
    "Code sandbox unavailable: Docker (or the zeus-arch image) was not found, and player code is not run directly on "
    "this computer by default. To enable the sandbox: install and start Docker, then run "
    "setup/build_sandbox.sh to build the zeus-arch image. (Unsafe alternative for a throwaway machine only: "
    "start the server with ULT_ALLOW_HOST_EXEC=1 to run code as your own user with no isolation.)"
)


def host_exec_allowed():
    """True only when the operator set ULT_ALLOW_HOST_EXEC to exactly "1" (read each call, never cached)."""
    return os.environ.get(HOST_EXEC_ENV) == "1"


def docker_available():
    """True when the docker CLI exists, the daemon answers, AND the zeus-arch image has been built.

    Checked with `docker info` and `docker image inspect` (10 s cap each). Never raises. A running Docker
    without the image counts as unavailable: the 503 message tells the player to build it.
    """
    if shutil.which("docker") is None:
        return False
    try:
        for cmd in (["docker", "info"], ["docker", "image", "inspect", SANDBOX_IMAGE]):
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if res.returncode != 0:
                return False
        return True
    except Exception:
        return False


def _hardening_flags():
    """Flags shared by the grading containers and the terminal container."""
    return [
        "--network", "none",
        "--memory", RUN_MEMORY,
        "--memory-swap", RUN_MEMORY,
        "--cpus", RUN_CPUS,
        "--pids-limit", RUN_PIDS_LIMIT,
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--user", RUN_USER,
    ]


def build_run_argv(chapter_id, container_name):
    """argv for one ephemeral grading container (pure function, unit-tested without Docker).

    Read-only root filesystem with a small tmpfs at /tmp for scratch; validators AND the player's files are
    mounted read-only, so player code cannot rewrite the validator that grades it.
    """
    return [
        "docker", "run", "--rm",
        "--name", container_name,
        *_hardening_flags(),
        "--read-only",
        "--tmpfs", "/tmp:rw,size=64m",
        "-e", "HOME=/tmp",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-v", f"{RELIC_SAVE_DIR}:/workspace:ro",
        "-v", f"{BUNDLED_SANDBOX_DIR}:/sandbox:ro",
        "-w", "/tmp",
        SANDBOX_IMAGE,
        "python", f"/sandbox/test_frameworks/ch{int(chapter_id)}_test.py",
    ]


def build_shell_container_argv():
    """argv for the long-lived terminal container (Alt+5): same limits, validators read-only.

    The player's workspace stays writable here (it is where they work); the root filesystem is not read-only
    because an interactive shell needs to write (pip, caches).
    """
    return [
        "docker", "run", "-d",
        "--name", SANDBOX_CONTAINER_NAME,
        *_hardening_flags(),
        "-v", f"{RELIC_SAVE_DIR}:/workspace",
        "-v", f"{BUNDLED_SANDBOX_DIR}:/sandbox:ro",
        "-w", "/workspace",
        SANDBOX_IMAGE,
        "tail", "-f", "/dev/null",
    ]


def kill_container(name):
    """Kills (and, via --rm, removes) a grading container by name. Best effort, never raises."""
    try:
        subprocess.run(["docker", "kill", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except Exception as e:
        logger.error(f"docker kill {name} failed: {e}")

# Where the project root is: normally the repo root; for a PyInstaller build the bundled read-only files live
# under sys._MEIPASS but the writable workspace must be the current directory.
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

# Player solution files; bind-mounted into the container as /workspace (read/write) so the validator sees what
# /api/compile wrote.
# Persistent directory storing user solution files accessible inside container volume
RELIC_SAVE_DIR = os.path.join(WORKSPACE_DIR, "save_data", "relic_save")


# Idempotent "make sure the container is up" in three escalating steps: already running -> done; exists but
# stopped -> `docker start`; missing -> `docker run -d` a long-lived idle container (`tail -f /dev/null` keeps
# it alive so each test is a fast `docker exec`, not a fresh container).
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
        # `docker inspect -f {{.State.Running}}` prints "true" or "false"; a non-zero exit code means the
        # container does not exist (or Docker is not running).
        # Step 1: Query Docker daemon to verify container existence and running state via inspect format string
        check_run = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", SANDBOX_CONTAINER_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if check_run.returncode == 0 and check_run.stdout.strip() == "true":
            return True

        # `ps -a` includes stopped containers; restarting keeps the same mounts, which avoids recreating
        # volumes.
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

        # Two bind mounts: user code (read/write, needed for solutions and chapter side effects) and
        # validators (/sandbox). The image tag zeus-arch:latest must already exist (built by
        # setup/build_sandbox.sh); if it does not, `docker run` fails and False is returned.
        logger.info("Launching new sandbox container...")
        run_cmd = build_shell_container_argv()
        run_proc = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if run_proc.returncode != 0:
            logger.error(f"Failed to launch container: {run_proc.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking/starting sandbox: {e}")
        return False


def require_execution_backend():
    """Raises SandboxUnavailable unless Docker works or host execution was explicitly enabled.

    Called by the route BEFORE the player's code is written to disk.
    """
    if docker_available() or host_exec_allowed():
        return
    raise SandboxUnavailable(UNAVAILABLE_MESSAGE)


def _run_host(chapter_id):
    """UNSAFE opt-in path: runs the validator (which execs the player's file) on the host as this user."""
    logger.warning(
        "UNSAFE: ULT_ALLOW_HOST_EXEC=1 and Docker is unavailable. Running player code DIRECTLY ON THIS "
        "COMPUTER as the current user with no isolation. Unset ULT_ALLOW_HOST_EXEC and use Docker."
    )
    local_test_path = os.path.join(BUNDLED_SANDBOX_DIR, "test_frameworks", f"ch{int(chapter_id)}_test.py")
    if not os.path.exists(local_test_path):
        return {"success": False, "output": f"Test suite ch{chapter_id}_test.py not found."}
    try:
        res = subprocess.run(
            [sys.executable, local_test_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=RUN_TIMEOUT_SECONDS,
        )
        return {"success": res.returncode == 0, "output": res.stdout + res.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Execution timed out (15s limit). Infinite loop detected?"}
    except Exception as e:
        return {"success": False, "output": f"Local execution failed: {e}"}


def execute_test(chapter_id: int):
    """Runs the chapter validator for the player's saved solution.

    Returns:
        dict: {"success": bool, "output": str}.

    Raises:
        SandboxUnavailable: Docker is not usable and ULT_ALLOW_HOST_EXEC=1 is not set.
    """
    if not docker_available():
        if host_exec_allowed():
            return _run_host(chapter_id)
        raise SandboxUnavailable(UNAVAILABLE_MESSAGE)

    name = "ult-run-" + secrets.token_hex(6)
    argv = build_run_argv(chapter_id, name)
    try:
        res = subprocess.run(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=RUN_TIMEOUT_SECONDS,
        )
        output = res.stdout + res.stderr
        if res.returncode == 125 and "Unable to find image" in output:
            output += "\nBuild the sandbox image first: setup/build_sandbox.sh"
        return {"success": res.returncode == 0, "output": output}
    except subprocess.TimeoutExpired:
        # Killing only the docker CLI would leave the loop running inside the container: kill it by name.
        kill_container(name)
        return {"success": False, "output": "Execution timed out in the sandbox (15s limit); the container was killed."}
    except Exception as e:
        kill_container(name)
        return {"success": False, "output": f"Docker run failed: {e}"}
