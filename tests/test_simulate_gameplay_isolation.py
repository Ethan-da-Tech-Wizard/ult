"""Regression test: scripts/simulate_gameplay.py must run its server against a temporary save database.

Before the fix the child server inherited no ZEUS_SAVE_DB_PATH, so every simulated run wrote 22 checkpoint
rows into the player's real save_data/save_state.db. The test swaps subprocess.Popen for a recorder (no
server is started) and checks the environment handed to the child.

Run: python3 tests/test_simulate_gameplay_isolation.py
"""

import importlib.util
import os
import sys
import tempfile
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_module():
    """Imports scripts/simulate_gameplay.py by path (scripts/ is not a package)."""
    spec = importlib.util.spec_from_file_location("simulate_gameplay", os.path.join(ROOT, "scripts", "simulate_gameplay.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    sim = load_module()
    captured = {}

    class FakeProc:
        """Stands in for the server process: exits cleanly when terminated."""

        def poll(self):
            return None

        def terminate(self):
            pass

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    def fake_popen(cmd, **kwargs):
        # The only thing under test is the environment given to the child.
        captured["env"] = kwargs["env"]
        return FakeProc()

    # Start from an environment that has no override, as a normal developer shell would.
    clean_env = {k: v for k, v in os.environ.items() if k != "ZEUS_SAVE_DB_PATH"}
    with mock.patch.dict(os.environ, clean_env, clear=True), \
            mock.patch.object(sim.subprocess, "Popen", fake_popen), \
            mock.patch.object(sim, "wait_for_server", side_effect=RuntimeError("stop after launch")):
        try:
            sim.main()
        except RuntimeError:
            pass  # expected: we abort right after the server "starts"

    db_path = captured["env"].get("ZEUS_SAVE_DB_PATH")
    assert db_path, "child server was started without ZEUS_SAVE_DB_PATH -> would use the real save DB"
    real = os.path.join(ROOT, "save_data", "save_state.db")
    assert os.path.abspath(db_path) != real, "temp DB path must not be the real save"
    assert os.path.abspath(db_path).startswith(os.path.realpath(tempfile.gettempdir())) or \
        os.path.abspath(db_path).startswith(tempfile.gettempdir()), f"not in a temp dir: {db_path}"
    assert not os.path.exists(os.path.dirname(db_path)), "temp dir should be cleaned up after the run"
    print("PASS test_simulate_gameplay_isolation:", db_path)


if __name__ == "__main__":
    sys.exit(main())
