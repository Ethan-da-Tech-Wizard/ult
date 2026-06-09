#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_URL = "http://127.0.0.1:8000"


def request_json(path, method="GET", payload=None, timeout=10):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def wait_for_server(proc, timeout=20):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        try:
            health = request_json("/api/health", timeout=2)
            if health.get("status") == "ok":
                return
        except Exception as exc:
            last_error = exc
            time.sleep(0.4)
    raise RuntimeError(f"server did not become healthy: {last_error}")


def main():
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except Exception as exc:
        print(f"Missing server dependency: {exc}")
        print("Run: python3 -m pip install -r requirements.txt")
        return 2

    with tempfile.TemporaryDirectory(prefix="sacred-tech-smoke-") as tmp_dir:
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

            diagnostics = request_json("/api/diagnostics")
            missing = diagnostics.get("missing_validators", [])
            if missing:
                raise AssertionError(f"missing validators: {missing}")
            print(f"[PASS] validators present: {len(diagnostics.get('validators_found', []))}")

            save_payload = {
                "gold": 321,
                "compute_tokens": 123,
                "unlocked_chapters": "0,1,2",
                "active_lead": "Low-Level Optimizer",
                "inventory_json": json.dumps(["contract:0", "item:patch_potion", "veridicus_defeated"]),
                "stats_json": json.dumps([
                    {"name": "Optimizer", "class": "Low-Level Optimizer", "level": 2, "exp": 10, "next_exp": 135, "hp": 120, "max_hp": 130, "atk": 20, "def": 11, "spd": 14, "luc": 8}
                ]),
                "state_json": json.dumps({
                    "currentChapter": 2,
                    "x": 9,
                    "y": 8,
                    "openedChests": ["2:10,4"],
                    "readManuals": ["python-field-manual", "sql-survival-guide"],
                }),
            }
            request_json("/api/save", method="POST", payload=save_payload)
            saved = request_json("/api/save")
            saved_state = json.loads(saved.get("state_json", "{}"))
            assert saved.get("gold") == 321
            assert saved_state.get("currentChapter") == 2
            assert "2:10,4" in saved_state.get("openedChests", [])
            assert "sql-survival-guide" in saved_state.get("readManuals", [])
            print("[PASS] save/load persistence")

            failures = []
            for chapter_id in range(22):
                code_data = request_json(f"/api/code?chapter_id={chapter_id}", timeout=10)
                result = request_json(
                    "/api/compile",
                    method="POST",
                    payload={"chapter_id": chapter_id, "code": code_data.get("code", "")},
                    timeout=30,
                )
                if not result.get("success"):
                    failures.append((chapter_id, result.get("output", "")))
                else:
                    print(f"[PASS] chapter {chapter_id} compile")

            if failures:
                for chapter_id, output in failures:
                    print(f"[FAIL] chapter {chapter_id}\n{output}")
                raise AssertionError(f"{len(failures)} chapter compile checks failed")

            print("[PASS] full-stack smoke complete")
            return 0
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
