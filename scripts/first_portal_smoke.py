#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile

from full_stack_smoke import ROOT_DIR, request_json, wait_for_server


def main():
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except Exception as exc:
        print(f"Missing server dependency: {exc}")
        print("Run: python3 -m pip install -r requirements.txt")
        return 2

    with tempfile.TemporaryDirectory(prefix="sacred-tech-first-portal-") as tmp_dir:
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT_DIR
        env["ZEUS_SAVE_DB_PATH"] = os.path.join(tmp_dir, "save_state.db")
        proc = subprocess.Popen(
            [sys.executable, os.path.join(ROOT_DIR, "server", "main.py")],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        try:
            wait_for_server(proc)
            print("[PASS] server health")

            initial = request_json("/api/save")
            initial_state = json.loads(initial.get("state_json", "{}"))
            assert initial_state.get("screenMode") == "dark"
            assert initial_state.get("currentChapter") == 0
            print("[PASS] fresh save starts at dark Chapter 0")

            code_data = request_json("/api/code?chapter_id=0")
            compile_result = request_json(
                "/api/compile",
                method="POST",
                payload={"chapter_id": 0, "code": code_data.get("code", "")},
                timeout=30,
            )
            assert compile_result.get("success"), compile_result.get("output", "")
            print("[PASS] Chapter 0 compile restores the gate")

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
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
