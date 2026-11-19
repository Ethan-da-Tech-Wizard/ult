#!/usr/bin/env python3

# ==============================================================================
# Program: first_portal_smoke.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: End-to-end integration smoke test exercising Chapter 0 and Chapter 1 runtime contracts.
#          Spawns an isolated background FastAPI backend with an ephemeral temporary SQLite database,
#          polls health check endpoints, validates baseline save state schemas, confirms that
#          untouched skeleton templates are rejected, and validates that correct PATH solutions
#          unlock the Chapter 1 portal while accurately persisting inventory across reloads.
# ==============================================================================

# How this file fits the app: CI job "First portal smoke" (python scripts/first_portal_smoke.py). A shorter, more targeted cousin of full_stack_smoke.py that checks the opening of the game: a fresh save starts at Chapter 0 in dark mode, the raw Chapter 0 template is rejected, the correct PATH solution passes, and a Chapter 1 save with tutorial inventory flags survives a reload.
# Reuses ROOT_DIR/request_json/wait_for_server from full_stack_smoke.py (same directory, so the import works when run as a script). Exit codes as in full_stack_smoke.py.

import json
import os
import subprocess
import sys
import tempfile

from full_stack_smoke import ROOT_DIR, request_json, wait_for_server


def main():
    """Main smoke test pipeline executing the Chapter 0 to Chapter 1 verification sequence."""

    # Dependency pre-flight (exit code 2 = environment problem, not a test failure).
    # Pre-flight check: ensure required HTTP backend libraries are importable
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except Exception as exc:
        print(f"Missing server dependency: {exc}")
        print("Run: python3 -m pip install -r requirements.txt")
        return 2

    # Execute inside an isolated temporary directory to ensure test isolation

    # Temporary save DB keeps the real save untouched and makes "fresh save" assertions deterministic.
    with tempfile.TemporaryDirectory(prefix="sacred-tech-first-portal-") as tmp_dir:
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT_DIR
        env["ZEUS_SAVE_DB_PATH"] = os.path.join(tmp_dir, "save_state.db")
        
        # Spawn backend FastAPI daemon process
        proc = subprocess.Popen(
            [sys.executable, os.path.join(ROOT_DIR, "server", "main.py")],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        try:
            # 1. Wait for server loopback socket to respond to health probes
            wait_for_server(proc)
            print("[PASS] server health")

            # Defaults come from init_db() in server/main.py: dark screen mode and chapter 0.
            # 2. Verify initial default player state (dark mode, chapter 0)
            initial = request_json("/api/save")
            initial_state = json.loads(initial.get("state_json", "{}"))
            assert initial_state.get("screenMode") == "dark"
            assert initial_state.get("currentChapter") == 0
            print("[PASS] fresh save starts at dark Chapter 0")

            # The validator must reject the unmodified starter template (otherwise every chapter would count as solved from the start).
            # 3. Security Boundary: The raw skeleton must be rejected by validator
            skeleton_data = request_json("/api/code?chapter_id=0&skeleton=1")
            skeleton_result = request_json(
                "/api/compile",
                method="POST",
                payload={"chapter_id": 0, "code": skeleton_data.get("code", "")},
                timeout=30,
            )
            assert not skeleton_result.get("success"), "Chapter 0 skeleton should not pass untouched"
            print("[PASS] Chapter 0 skeleton correctly rejected")

            # The accepted answer appends /usr/local/bin to PATH, the Chapter 0 lesson ("restore the toolchain").
            # 4. Verification: Submit valid PATH extension statement and assert success
            compile_result = request_json(
                "/api/compile",
                method="POST",
                payload={"chapter_id": 0, "code": 'export PATH=$PATH:/usr/local/bin\necho "Booting environment..."\n'},
                timeout=30,
            )
            assert compile_result.get("success"), compile_result.get("output", "")
            print("[PASS] Chapter 0 compile restores the gate")

            # Inventory flag names mirror the item/tutorial keys that client/app.js stores in the player's inventory; they are plain strings to the server, so this test only proves persistence, not game logic.
            # 5. Persistence: Post updated save state unlocking Chapter 1
            inventory = [
                "contract:0",
                "opening_hints_seen",
                "tutorial_library_unlocked",
                "tutorial_compiler_smith_talked",
                "tutorial_first_portal_reward_seen",
            ]
            save_payload = {
                "gold": initial.get("gold", 200),
                "compute_tokens": initial.get("compute_tokens", 100),
                "unlocked_chapters": "0,1",
                "active_lead": initial.get("active_lead", "Low-Level Optimizer"),
                "inventory_json": json.dumps(inventory),
                "stats_json": initial.get("stats_json", "{}"),
                "state_json": json.dumps({
                    "currentChapter": 1,
                    "x": 1,
                    "y": 7,
                    "openedChests": [],
                    "readManuals": ["python-field-manual"],
                    "readManualPages": ["python-field-manual:0"],
                    "screenMode": "color",
                    "lastSavedAt": "2026-06-09T00:00:00.000Z",
                }),
            }
            request_json("/api/save", method="POST", payload=save_payload)
            
            # Read the save back from SQLite through the API and compare each field, which catches serialisation or column-migration bugs.
            # 6. Verification: Reload save state from SQLite and assert field roundtrip
            reloaded = request_json("/api/save")
            reloaded_state = json.loads(reloaded.get("state_json", "{}"))
            reloaded_inventory = json.loads(reloaded.get("inventory_json", "[]"))

            assert reloaded.get("unlocked_chapters") == "0,1"
            assert "contract:0" in reloaded_inventory
            assert "tutorial_first_portal_reward_seen" in reloaded_inventory
            assert reloaded_state.get("currentChapter") == 1
            assert reloaded_state.get("screenMode") == "color"
            assert "python-field-manual:0" in reloaded_state.get("readManualPages", [])
            print("[PASS] first portal save/reload preserves route progress")
            return 0
        finally:
            # Terminate and reap server subprocess
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
